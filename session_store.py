from os import urandom
from base64 import b64encode

class SessionStore():
	""" Stores session data. """

	def __init__(self):
		self.sessions = {}

	def generate_session_id(self):
		r = urandom(32)
		return b64encode(r).decode("utf-8")

	def create_session(self):
		sessionId = self.generate_session_id()
		self.sessions[sessionId] = {}
		return sessionId

	def get_session(self, session_id):
		if session_id in self.sessions:
			return self.sessions[session_id]
		return None

	# cleanup possibly
