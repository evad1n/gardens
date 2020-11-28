#! /usr/bin/python3

from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import json
import sys
from passlib.hash import bcrypt
from http import cookies

# Fix hanging
from socketserver import ThreadingMixIn

from garden_db import GardensDB
from session_store import SessionStore

STORE = SessionStore()


class GardensHTTPRequestHandler(BaseHTTPRequestHandler):
    """ The HTTP request handler for the gardens app. """

    # HTTP METHODS
    def do_OPTIONS(self):
        """ Handle OPTIONS requests. Specififes allowed methods/headers. """
        self.load_session()
        self.send_response(200)
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header("Access-Control-Allow-Origin", "null")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_cookie()
        self.end_headers()

    def do_GET(self):
        """ Handle GET requests. """
        self.load_session()
        parts = self.path.split('/')
        collection = parts[1]
        if collection == "gardens":
            if len(parts) > 2:
                garden_id = parts[2]
                self.get_one_garden(garden_id)
            else:
                self.get_gardens()
        elif collection == "me" and len(parts) == 2:
            self.get_user_data()
        else:
            self.response(404)

    def do_POST(self):
        """ Handle POST requests. """
        self.load_session()
        if self.path == "/gardens":
            self.add_garden()
        elif self.path == "/comments":
            self.add_comment()
        elif self.path == "/flowers":
            self.add_flower()
        elif self.path == "/users":
            self.add_user()
        elif self.path == "/sessions":
            self.create_session()
        else:
            self.response(404)

    def do_PUT(self):
        """ Handle PUT requests. """
        self.load_session()
        parts = self.path.split('/')
        if len(parts) < 3:
            self.response(404)
        collection = parts[1]
        id = parts[2]
        if collection == "gardens":
            self.update_garden(id)
        elif collection == "comments":
            self.delete_comment(id)
        else:
            self.response(404)

    def do_DELETE(self):
        """ Handle DELETE requests. """
        self.load_session()

        # Short circuit for logout case
        if self.path == "/sessions":
            self.delete_session()
            return

        parts = self.path.split('/')
        if len(parts) < 3:
            self.response(404)
        collection = parts[1]
        id = parts[2]
        if collection == "gardens":
            self.delete_garden(id)
        elif collection == "comments":
            self.delete_comment(id)
        elif collection == "flowers":
            self.delete_flower(id)
        else:
            self.response(404)


    # HELPER METHODS
    def decode(self):
        """ Parses the request for URL search parameters and returns them in dict format. """
        length = self.headers['Content-Length']
        body = parse_qs(self.rfile.read(int(length)).decode("utf-8"))
        return body

    def response(self, status_code, body=False):
        """ Sends a response with the specified status code with cors headers. Allows for json body. Also sends the cookie. """
        self.send_response(status_code)
        if body:
            self.send_header("Content-Type", "application/json")
        self.send_cookie()
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.end_headers()


    # COOKIES
    def get_cookie(self):
        """ Returns the cookie in the headers, or creates a new one if there is none. """
        if "Cookie" in self.headers:
            self.cookie = cookies.SimpleCookie(self.headers['Cookie'])
        else:
            self.cookie = SimpleCookie()

    def send_cookie(self):
        for morsel in self.cookie.values():
            self.send_header("Set-Cookie", morsel.OutputString())


    # SESSIONS
    def create_session(self):
        """ Attempts to login and authenticate. """
        DB = GardensDB()
        body = self.decode()
        reqEmail = body['email'][0]
        reqPassword = body['password'][0]

        # check password
        user = DB.get_user(reqEmail)
        if user != None:
            if bcrypt.verify(reqPassword, user['password']):
                self.session_data['uid'] = user['id']
                self.response(201, True)
            else:
                self.response(401)
        else:
            self.response(401)


    def load_session(self):
        self.get_cookie()
        if 'sessionId' in self.cookie:
            session_id = self.cookie['sessionId'].value
            data = STORE.get_session(session_id)
            if data == None:
                session_id = STORE.create_session()
                data = STORE.get_session(session_id)
                self.cookie['sessionId'] = session_id
            self.session_data = data
        else:
            session_id = STORE.create_session()
            data = STORE.get_session(session_id)
            self.cookie['sessionId'] = session_id
            self.session_data = data

    def delete_session(self):
        """ Log the user out. """
        if 'uid'  in self.session_data:
            del self.session_data['uid']
        self.response(200)


    # USERS
    def add_user(self):
        """ Creates a new user with a unique email. """
        DB = GardensDB()
        body = self.decode()
        first_name = body['first_name'][0]
        last_name = body['last_name'][0]
        email = body['email'][0]
        password = body['password'][0]

        # check if email is duplicate
        user = DB.get_user(email)
        if user != None:
            self.response(422)
            return

        self.response(201, True)
        # hash password
        hashed = bcrypt.hash(password)
        DB.create_user(first_name, last_name, email, hashed)

    def get_user_data(self):
        """ Gets user data if logged in. """
        DB = GardensDB()
        if 'uid' not in self.session_data:
            self.response(401, True)
            self.wfile.write(bytes(json.dumps({'message': "Not authenticated"}), "utf-8"))
            return
        
        self.response(200, True)
        user_id = self.session_data['uid']
        user = DB.get_user_by_id(user_id)
        gardens = DB.get_user_gardens(user_id)
        self.wfile.write(bytes(json.dumps({'first_name': user['first_name'], 'last_name': user['last_name'], 'id': user['id'],'gardens': gardens}), "utf-8"))


    # GARDENS
    def add_garden(self):
        """ Creates a new garden with name and author. """
        DB = GardensDB()
        if 'uid' not in self.session_data:
            self.response(401)
            return
        userid = self.session_data['uid']
        self.response(201, True)
        body = self.decode()
        name = body['name'][0]
        author = body['author'][0]
        created_id = DB.create_garden(name, author, userid)
        self.wfile.write(bytes(json.dumps(created_id), "utf-8"))

    def get_gardens(self):
        """ Sends a list of all garden depth 0 information. """
        DB = GardensDB()
        self.response(200, True)
        data = DB.get_gardens()
        self.wfile.write(bytes(json.dumps(data), "utf-8"))

    def get_one_garden(self, id):
        DB = GardensDB()
        garden = DB.get_one_garden(id)
        if garden != None:
            self.response(200, True)
            self.wfile.write(bytes(json.dumps(garden), "utf-8"))
        else:
            self.response(404)

    def update_garden(self, id):
        DB = GardensDB()
        if 'uid' not in self.session_data:
            self.response(401)
            return

        garden = DB.get_one_garden(id)
        if garden != None:
            # If they are not the owner of this garden
            if self.session_data['uid'] != garden['userid']:
                self.response(403)
                return
            self.response(204)
            body = self.decode()
            name = body['name'][0]
            DB.update_garden(id, name)
        else:
            self.response(404)

    def delete_garden(self, id):
        DB = GardensDB()
        if 'uid' not in self.session_data:
            self.response(401)
            return
    
        garden = DB.get_one_garden(id)
        if garden != None:
            # If they are not the owner of this garden
            if self.session_data['uid'] != garden['userid']:
                self.response(403)
                return
            self.response(204)
            DB.delete_garden(id)
        else:
            self.response(404)


    # COMMENTS
    def add_comment(self):
        """ Adds a comment to a particular garden. """
        DB = GardensDB()
        if 'uid' not in self.session_data:
            self.response(401)
            return

        self.response(201)
        body = self.decode()
        garden_id = body['gardenId'][0]
        content = body['content'][0]
        user_id = self.session_data['uid']
        DB.create_comment(garden_id, content, user_id)

    def update_comment(self, id):
        DB = GardensDB()
        if 'uid' not in self.session_data:
            self.response(401)
            return

        comment = DB.get_one_comment(id)
        if comment != None:
            # If they did not write the comment
            if self.session_data['uid'] != comment['userid']:
                self.response(403)
                return
            self.response(204)
            body = self.decode()
            content = body['content'][0]
            DB.update_comment(id, content)
        else:
            self.response(404)

    def delete_comment(self, id):
        DB = GardensDB()
        if 'uid' not in self.session_data:
            self.response(401)
            return

        comment = DB.get_one_comment(id)
        if comment != None:
            # If they did not write the comment
            if self.session_data['uid'] != comment['userid']:
                self.response(403)
                return
            self.response(204)
            DB.delete_comment(id)
        else:
            self.response(404)


    # FLOWERS
    def add_flower(self):
        """ Adds a flower to a particular garden. """
        DB = GardensDB()
        if 'uid' not in self.session_data:
            self.response(401)
            return

        self.response(201)
        body = self.decode()
        garden_id = body['gardenId'][0]
        color = body['color'][0]
        x = body['x'][0]
        y = body['y'][0]
        DB.create_flower(garden_id, color, x, y)

    def delete_flower(self, id):
        DB = GardensDB()
        if 'uid' not in self.session_data:
            self.response(401)
            return

        flower = DB.get_one_flower(id)
        if flower != None:
            self.response(204)
            DB.delete_flower(id)
        else:
            self.response(404)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):

    pass

def run():
    """ Run server. """

    db = GardensDB()
    db.create_tables()
    db = None

    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    listen = ("0.0.0.0", port)
    server = ThreadedHTTPServer(listen, GardensHTTPRequestHandler)

    print(f"Server is listening on", "{}:{}...".format(*listen))
    server.serve_forever()


run()