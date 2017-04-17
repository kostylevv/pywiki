import webapp2

from google.appengine.ext import db

class User(db.Model):
	username = db.StringProperty(required = True)
	password = db.StringProperty(required = True)
	email = db.StringProperty(required = False)

class Page(db.Model):
	content = db.TextProperty(required = True)

