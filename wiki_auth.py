import os
import webapp2
import time
import hmac
import re
import random
import string
import hashlib

from wiki_utils import *
from wiki_models import User

from google.appengine.ext import db


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")  #regex for username
PASS_RE = re.compile(r"^.{3,20}$")  			#regex for password
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")	#regex for email adress


def is_user_signed_up(self):
		result = None
		cookie_str = self.request.cookies.get('user_id')
		if cookie_str:
			cookie_val = check_hmac_str(cookie_str)
			if cookie_val: 
				user = User.get_by_id(int(cookie_val))
				if user:
					result = user
		return result



class SignUp(Handler):
	def valid_username(self, username):
		return USER_RE.match(username)
	
	def valid_password(self, password):
		return PASS_RE.match(password)

	def valid_email(self, email):
		if email == '':
			return True
		else:
			return EMAIL_RE.match(email)

	def render_front(self, username="", email="", error=""):
		self.render("signup.html", username=username, email=email, error=error, 
			home="/", logout = "/logout", login = "/login", signup = "/signup")

	def post(self):
		username = self.request.get("username")
		password = self.request.get("password")
		verify = self.request.get("verify")
		email = self.request.get("email")
		valid = True
		error = ""

		if not self.valid_username(username):
			error += "Username is invalid. "
			valid = False
		else:
			posts = db.GqlQuery("SELECT * FROM User WHERE username='" + username+"'")
			if posts.count() > 0:
				error += "User already exists. "
				valid = False
		
		if password != verify:
			error += "Passwords don't match. "
			valid = False
		elif not self.valid_password(password):
			error += "Password is invalid. "
			valid = False

		if not self.valid_email(email):
			error += "E-mail is invalid"
			valid = False

		if valid:
			pwd = make_pw_hash(username, password, make_salt())
			user = User(username = username, email = email, password=pwd)
			user.put()
			user_id = str(user.key().id())
			self.response.headers.add_header('Set-Cookie', 'user_id=%s' % make_hmac_str(user_id))
			self.redirect("/")
		else:
			self.render_front(username,email,error)


	def get(self):
		user = is_user_signed_up(self)
		if user:
			self.redirect('/')
		else:
			self.render_front()

class Login(Handler):
	def valid_username(self, username):
		return USER_RE.match(username)
	
	def valid_password(self, password):
		return PASS_RE.match(password)

	def render_front(self, username="", error=""):
		self.render("login.html", username=username, error=error, home="/",
			logout = "/logout", login = "/login", signup = "/signup")

	def post(self):
		username = self.request.get("username")
		password = self.request.get("password")
		valid = True
		error = ""

		if not self.valid_username(username):
			error += "Username is invalid. "
			valid = False
		else:
			user = db.GqlQuery("SELECT * FROM User WHERE username='" + username+"'").get()
			if user == None:
				error += "User not found. "
				valid = False
			elif not self.valid_password(password):
				error += "Password is invalid. "
				valid = False
			elif not valid_pw(user.username, password, user.password):
				error += "Username and password don't match"
				valid = False

		if valid:
			self.response.headers.add_header('Set-Cookie', 'user_id=%s' % make_hmac_str(str(user.key().id())))
			self.redirect("/")
		else:
			self.render_front(username,error)


	def get(self):
		user = is_user_signed_up(self)
		if user:
			self.redirect('/')
		else:
			self.render_front()

def req_posts(update = False):
		key = 'recent'
		posts = memcache.get(key)

		if posts is None or update:
			logging.error("DB QUERY")
			posts = db.GqlQuery("SELECT * FROM Post ORDER BY submitted DESC")
			posts = list(posts)
			memcache.set(key, posts) 
			cur = time.time()
			memcache.set('gen',cur)
		return posts

class Logout(Handler):
	def get(self):
		user = is_user_signed_up(self)
		if user:
			self.response.delete_cookie('user_id')
			self.redirect("/")
		else:
			self.redirect("/")