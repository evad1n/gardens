#!/usr/bin/env python3

import sqlite3

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class GardensDB:
    """ The database API for the gardens web app. """
    
    def __init__(self):
        self.con = sqlite3.connect("gardens.db")
        self.con.row_factory = dict_factory
        self.cursor = self.con.cursor()
        # Allow foreign keys
        self.cursor.execute("PRAGMA foreign_keys = ON")
        self.con.commit()

    def get_last_id(self):
        """ Returns the last inserted id. """
        self.cursor.execute("SELECT last_insert_rowid()")
        return {"id": self.cursor.fetchone()["last_insert_rowid()"]}

    # USERS
    def create_user(self, first_name, last_name, email, password):
        """ Creates a user and stores the hashed password. """
        self.cursor.execute("INSERT INTO users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)", [first_name, last_name, email, password])
        self.con.commit()
        return self.get_last_id()
    
    def get_user(self, email):
        """ Returns the user's info. """
        self.cursor.execute("SELECT * FROM users WHERE email = (?)", [email])
        return self.cursor.fetchone()

    def get_user_by_id(self, uid):
        """ Returns the user's info. """
        self.cursor.execute("SELECT * FROM users WHERE id = (?)", [uid])
        return self.cursor.fetchone()

    # GARDENS
    def create_garden(self, name, author, userid):
        """ Creates a garden and returns the id of the created garden. """
        data = [name, author, userid]
        self.cursor.execute("INSERT INTO gardens (name, author, author_id) VALUES (?, ?, ?)", data)
        self.con.commit()
        return self.get_last_id()

    def get_gardens(self):
        """ Returns dict of garden info. """
        self.cursor.execute("SELECT * FROM gardens")
        return self.cursor.fetchall()


    def get_user_gardens(self, userid):
        """ Returns all gardens created by a user. """
        self.cursor.execute("SELECT * FROM gardens WHERE author_id = (?)", [userid])
        return self.cursor.fetchall()

    def get_one_garden(self, id):
        """ Returns dict of specific garden info, including comments and flowers. """
        self.cursor.execute("SELECT * FROM gardens WHERE id = (?)", [id])
        data = self.cursor.fetchone()
        if data != None:
            data['comments'] = self.get_comments(id)
            data['flowers'] = self.get_flowers(id)
        return data

    def update_garden(self, id, name):
        self.cursor.execute("UPDATE gardens SET name = ? WHERE id = ?", [name, id])
        self.con.commit()

    def delete_garden(self, id):
        self.cursor.execute("DELETE FROM gardens WHERE id = ?", [id])
        self.con.commit()
        
    # COMMENTS
    def create_comment(self, garden_id, comment, user_id):
        data = [comment, garden_id, user_id]
        self.cursor.execute("INSERT INTO comments (content, garden_id, author_id) VALUES (?, ?, ?)", data)
        self.con.commit()
        return self.get_last_id()

    def get_comments(self, garden_id):
        """ Returns all comments from the garden with {id = garden_id} """
        self.cursor.execute("SELECT c.id, c.content, u.first_name AS author, c.author_id FROM comments c \
            INNER JOIN users u ON u.id = c.author_id WHERE c.garden_id = (?)", [garden_id])
        return self.cursor.fetchall()

    def get_one_comment(self, id):
        self.cursor.execute("SELECT * FROM comments WHERE id = ?", [id])
        return self.cursor.fetchone()

    def update_comment(self, id, content):
        self.cursor.execute("UPDATE comments SET content = ? WHERE id = ?", [content, id])
        self.con.commit()

    def delete_comment(self, id):
        self.cursor.execute("DELETE FROM comments WHERE id = (?)", [id])
        self.con.commit()

    # FLOWERS
    def create_flower(self, garden_id, color, x, y):
        data = [color, x, y, garden_id]
        self.cursor.execute("INSERT INTO flowers (color, x, y, garden_id) VALUES (?, ?, ?, ?)", data)
        self.con.commit()
        return self.get_last_id()

    def get_flowers(self, garden_id):
        """ Returns all flowers from the garden with {id = garden_id} """
        self.cursor.execute("SELECT * FROM flowers WHERE garden_id = (?)", [garden_id])
        return self.cursor.fetchall()

    def get_one_flower(self, id):
        self.cursor.execute("SELECT * FROM flowers WHERE id = ?", [id])
        return self.cursor.fetchone()

    def delete_flower(self, id):
        self.cursor.execute("DELETE FROM flowers WHERE id = (?)", [id])
        self.con.commit()
