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
        # For multiple domains, echo back the self.headers['Origin']
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Accept, Content-Type, Origin")
        self.send_cookie()
        self.end_headers()

    def do_GET(self):
        """ Handle GET requests. """
        self.load_session()
        coll, id, valid = self.parse_path()
        if not valid:
            self.response(404)

        if coll == "gardens":
            if id:
                self.get_one_garden(id)
            else:
                self.get_gardens()
        elif coll == "me" and not id:
            self.get_user_data()
        else:
            self.response(404)

    def do_POST(self):
        """ Handle POST requests. """
        self.load_session()
        coll, id, valid = self.parse_path()
        if not valid or id:
            self.response(404)

        if coll == "gardens":
            self.add_garden()
        elif coll == "comments":
            self.add_comment()
        elif coll == "flowers":
            self.add_flower()
        elif coll == "users":
            self.add_user()
        elif coll == "sessions":
            self.create_session()
        else:
            self.response(404)

    def do_PUT(self):
        """ Handle PUT requests. """
        self.load_session()
        coll, id, valid = self.parse_path()
        if not valid:
            self.response(404)

        if coll == "gardens" and id:
            self.update_garden(id)
        elif coll == "comments" and id:
            self.delete_comment(id)
        else:
            self.response(404)

    def do_DELETE(self):
        """ Handle DELETE requests. """
        self.load_session()
        coll, id, valid = self.parse_path()
        if not valid:
            self.response(404)

        if coll == "sessions" and not id:
            self.delete_session()
        elif coll == "gardens" and id:
            self.delete_garden(id)
        elif coll == "comments" and id:
            self.delete_comment(id)
        elif coll == "flowers" and id:
            self.delete_flower(id)
        else:
            self.response(404)


    # HELPER METHODS

    def parse_path(self):
        """ Gets the resource collection and id from the request path. If it is not valid then valid will be False. """
        bad = (0, 0, False)

        if not self.path.startswith("/"):
            return bad
        # Skip first /
        parts = self.path[1:].split("/")
        # Throw away anything with too many parameters
        if len(parts) > 2:
            return bad

        collection = parts[0]
        id = None
        if len(parts) > 1:
            # Make sure type is int
            try:
                id = int(parts[1])
            except:
                return bad
        return (collection, id, True)


    def decode(self):
        """ Parses the request for URL search parameters and returns them in dict format. """
        length = self.headers['Content-Length']
        body = parse_qs(self.rfile.read(int(length)).decode("utf-8"))
        for key in body:
            body[key] = body[key][0]
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

    def no_auth(self, status_code):
        """ Generic messages for no authentication/authorization. """
        self.response(status_code, True)
        if status_code == 401:
            self.wfile.write(bytes(json.dumps({'message': "Not authenticated"}), "utf-8"))
        elif status_code == 403:
            self.wfile.write(bytes(json.dumps({'message': "Can only modify owned resources"}), "utf-8"))



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
        reqEmail = body['email']
        reqPassword = body['password']

        # check password
        user = DB.get_user(reqEmail)
        if user != None:
            if bcrypt.verify(reqPassword, user['password']):
                self.session_data['uid'] = user['id']
                self.response(201, True)
            else:
                self.no_auth(401)
        else:
            self.no_auth(401)


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
        first_name = body['first_name']
        last_name = body['last_name']
        email = body['email']
        password = body['password']

        # check if email is duplicate
        user = DB.get_user(email)
        if user != None:
            self.response(422, True)
            self.wfile.write(bytes(json.dumps({'message': "No duplicate email"}), "utf-8"))
            return

        # hash password
        hashed = bcrypt.hash(password)
        DB.create_user(first_name, last_name, email, hashed)
        self.response(201, True)

    def get_user_data(self):
        """ Gets user data if logged in. """
        DB = GardensDB()
        if 'uid' not in self.session_data:
            self.no_auth(401)
            return
        
        user_id = self.session_data['uid']
        user = DB.get_user_by_id(user_id)
        gardens = DB.get_user_gardens(user_id)
        self.response(200, True)
        self.wfile.write(bytes(json.dumps({'first_name': user['first_name'], 'last_name': user['last_name'], 'id': user['id'],'gardens': gardens}), "utf-8"))


    # GARDENS

    def add_garden(self):
        """ Creates a new garden with name and author. """
        DB = GardensDB()
        if 'uid' not in self.session_data:
            self.no_auth(401)
            return
        uid = self.session_data['uid']
        body = self.decode()
        name = body['name']
        author = body['author']
        created_id = DB.create_garden(name, author, uid)
        self.response(201, True)
        self.wfile.write(bytes(json.dumps(created_id), "utf-8"))

    def get_gardens(self):
        """ Sends a list of all garden depth 0 information. """
        DB = GardensDB()
        data = DB.get_gardens()
        self.response(200, True)
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
            self.no_auth(401)
            return

        garden = DB.get_one_garden(id)
        if garden != None:
            # If they are not the owner of this garden
            if self.session_data['uid'] != garden['author_id']:
                self.no_auth(403)
                return
            body = self.decode()
            name = body['name']
            DB.update_garden(id, name)
            self.response(204)
        else:
            self.response(404)

    def delete_garden(self, id):
        DB = GardensDB()
        if 'uid' not in self.session_data:
            self.no_auth(401)
            return
    
        garden = DB.get_one_garden(id)
        if garden != None:
            # If they are not the owner of this garden
            if self.session_data['uid'] != garden['author_id']:
                self.no_auth(403)
                return
            DB.delete_garden(id)
            self.response(204)
        else:
            self.response(404)


    # COMMENTS

    def add_comment(self):
        """ Adds a comment to a particular garden. """
        DB = GardensDB()
        if 'uid' not in self.session_data:
            self.no_auth(401)
            return

        body = self.decode()
        garden_id = body['gardenId']
        content = body['content']
        user_id = self.session_data['uid']
        DB.create_comment(garden_id, content, user_id)
        self.response(201)

    def update_comment(self, id):
        DB = GardensDB()
        if 'uid' not in self.session_data:
            self.no_auth(401)
            return

        comment = DB.get_one_comment(id)
        if comment != None:
            # If they did not write the comment
            if self.session_data['uid'] != comment['author_id']:
                self.no_auth(403)
                return
            body = self.decode()
            content = body['content']
            DB.update_comment(id, content)
            self.response(204)
        else:
            self.response(404)

    def delete_comment(self, id):
        DB = GardensDB()
        if 'uid' not in self.session_data:
            self.no_auth(401)
            return

        comment = DB.get_one_comment(id)
        if comment != None:
            # If they did not write the comment
            if self.session_data['uid'] != comment['author_id']:
                self.no_auth(403)
                return
            DB.delete_comment(id)
            self.response(204)
        else:
            self.response(404)


    # FLOWERS

    def add_flower(self):
        """ Adds a flower to a particular garden. """
        DB = GardensDB()
        if 'uid' not in self.session_data:
            self.no_auth(401)
            return

        body = self.decode()
        garden_id = body['gardenId']
        color = body['color']
        x = body['x']
        y = body['y']
        DB.create_flower(garden_id, color, x, y)
        self.response(201)

    def delete_flower(self, id):
        DB = GardensDB()
        if 'uid' not in self.session_data:
            self.no_auth(401)
            return

        flower = DB.get_one_flower(id)
        if flower != None:
            # If they are not the owner of this garden
            garden = DB.get_one_garden(flower['garden_id'])
            if self.session_data['uid'] != garden['author_id']:
                self.no_auth(403)
                return
            DB.delete_flower(id)
            self.response(204)
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

    print(f"Server is listening on", "http://{}:{}...".format(*listen))
    server.serve_forever()


run()