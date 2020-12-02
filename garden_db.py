#!/usr/bin/env python3

import os
import psycopg2
import psycopg2.extras
import urllib.parse

class GardensDB:
    """ The database API for the gardens web app. """
    
    def __init__(self):
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])

        self.con = psycopg2.connect(
            cursor_factory=psycopg2.extras.RealDictCursor,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        self.con.autocommit = True

        self.cursor = self.con.cursor()

    def __del__(self):
        self.con.close()

    def create_tables(self):
        """ Create the tables in the database for initial use. Will NOT drop old tables. """
        with open("schema.sql", "r") as f:
            self.cursor.execute(f.read())

    def reset(self):
        """ Reset the tables in the database. Will drop old tables and recreate them. Deletes ALL data. """
        with open("delete-tables.sql", "r") as f:
            self.cursor.execute(f.read())
        with open("schema.sql", "r") as f:
            self.cursor.execute(f.read())

    # USERS
    def create_user(self, first_name, last_name, email, password):
        """ Creates a user and stores the hashed password. """
        self.cursor.execute("INSERT INTO users (first_name, last_name, email, password) VALUES (%s, %s, %s, %s) RETURNING id", [first_name, last_name, email, password])
        rid = self.cursor.fetchone()
        return rid
    
    def get_user(self, email):
        """ Returns the user's info. """
        self.cursor.execute("SELECT * FROM users WHERE email = (%s)", [email])
        return self.cursor.fetchone()

    def get_user_by_id(self, uid):
        """ Returns the user's info. """
        self.cursor.execute("SELECT * FROM users WHERE id = (%s)", [uid])
        return self.cursor.fetchone()

    # GARDENS
    def create_garden(self, name, author, userid):
        """ Creates a garden and returns the id of the created garden. """
        data = [name, author, userid]
        self.cursor.execute("INSERT INTO gardens (name, author, author_id) VALUES (%s, %s, %s) RETURNING id", data)
        rid = self.cursor.fetchone()
        return rid

    def get_gardens(self):
        """ Returns dict of garden info. """
        self.cursor.execute("SELECT * FROM gardens")
        return self.cursor.fetchall()


    def get_user_gardens(self, userid):
        """ Returns all gardens created by a user. """
        self.cursor.execute("SELECT * FROM gardens WHERE author_id = (%s)", [userid])
        return self.cursor.fetchall()

    def get_one_garden(self, id):
        """ Returns dict of specific garden info, including comments and flowers. """
        self.cursor.execute("SELECT * FROM gardens WHERE id = (%s)", [id])
        data = self.cursor.fetchone()
        if data != None:
            data['comments'] = self.get_comments(id)
            data['flowers'] = self.get_flowers(id)
        return data

    def update_garden(self, id, name):
        self.cursor.execute("UPDATE gardens SET name = %s WHERE id = %s", [name, id])

    def delete_garden(self, id):
        self.cursor.execute("DELETE FROM gardens WHERE id = %s", [id])
        
    # COMMENTS
    def create_comment(self, garden_id, comment, user_id):
        data = [comment, garden_id, user_id]
        self.cursor.execute("INSERT INTO comments (content, garden_id, author_id) VALUES (%s, %s, %s) RETURNING id", data)
        rid = self.cursor.fetchone()
        return rid

    def get_comments(self, garden_id):
        """ Returns all comments from the garden with {id = garden_id} """
        self.cursor.execute("SELECT c.id, c.content, u.first_name AS author, c.author_id FROM comments c \
            INNER JOIN users u ON u.id = c.author_id WHERE c.garden_id = (%s)", [garden_id])
        return self.cursor.fetchall()

    def get_one_comment(self, id):
        self.cursor.execute("SELECT * FROM comments WHERE id = %s", [id])
        return self.cursor.fetchone()

    def update_comment(self, id, content):
        self.cursor.execute("UPDATE comments SET content = %s WHERE id = %s", [content, id])

    def delete_comment(self, id):
        self.cursor.execute("DELETE FROM comments WHERE id = (%s)", [id])

    # FLOWERS
    def create_flower(self, garden_id, color, x, y):
        data = [color, x, y, garden_id]
        self.cursor.execute("INSERT INTO flowers (color, x, y, garden_id) VALUES (%s, %s, %s, %s) RETURNING id", data)
        rid = self.cursor.fetchone()
        return rid

    def get_flowers(self, garden_id):
        """ Returns all flowers from the garden with {id = garden_id} """
        self.cursor.execute("SELECT * FROM flowers WHERE garden_id = (%s)", [garden_id])
        return self.cursor.fetchall()

    def get_one_flower(self, id):
        self.cursor.execute("SELECT * FROM flowers WHERE id = %s", [id])
        return self.cursor.fetchone()

    def delete_flower(self, id):
        self.cursor.execute("DELETE FROM flowers WHERE id = (%s)", [id])
