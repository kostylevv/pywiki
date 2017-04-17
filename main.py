import os
import webapp2
import jinja2
import time
import re
import string

from wiki_utils import *
from wiki_models import *
from wiki_auth import *

from datetime import date

from google.appengine.ext import db


"""
Wiki-like Google App Engine web application for Udacity Web Development course.

Implemented basic wiki functionality:
 - user authentication
 - creation and editing of pages (for registred users)
 - page editing history

@Autor Vladislav Kostylev 
@Email kostylev.v@gmail.com

"""

PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'							#regex for page name
HOME_PAGE_ID = "_main_"											#ID of a home page, which is an empty string 
																#This ID is intended to store entity in DB

class WikiPage(Handler):
	"""

		Class for handling of page viewing

	"""

	def render_front(self, content="", user = "", context_action = ""):
		"""
		Renders a wiki page.
    	
    	Args:
        content: Page content.
        user: A logged in user.
        context_action: A link to edit a page (shown in the page header)
    
		"""
		self.render("page.html", content=content, user = user, 
					 logout = "/logout", login = "/login", 
					 signup = "/signup", context_action = context_action, 
					 context_action_name = "Edit")
	
	def get(self, page_title = ""):
		page_title = page_title.strip('/\t\n\r') 				#trim and remove slash from GET page_title param

		context_action = '/_edit/' + page_title  				#generate link to edit page, which is shown
												 				#in the page header

		if page_title == "":					 				#empty string means that this is a home page
			page_title = HOME_PAGE_ID			 				#assign ID of a home page in that case

		page = Page.get_by_key_name(page_title)  				#Query for an entity by a page_title key

		if page is not None:					 				#check is page exists in DB			 

			user = is_user_signed_up(self)		 				#then check if user signed in
			
			if user:							 				#if signed in, pass content, user and 
				self.render_front(content = page.content, 		#context action link to render
				user = user, context_action = context_action)   			 
			else:
				self.render_front(content = page.content, 
				context_action = context_action) 				#otherwise, pass content 
																#and context action link only
					
		else:									 				#if page doesn't exist, 
			self.redirect('/_edit/'+page_title)					#redirect to editing page
			
		
class EditPage(Handler):
	def render_front(self, content="", user = "", context_action = ""):
		self.render("edit.html", content=content, user = user,
			logout = "/logout", login = "/login", context_action = context_action,
			context_action_name = "View") 

	def get(self, page_title = ""):
		"""
		Renders an editing page.
    	
    	Args:
        content: Page content.
        user: A logged in user.
        context_action: A link to edit a page (shown in the page header)
    
		"""
		user = is_user_signed_up(self)							#checking if user is logged in 

		if user:												#if yes:
			page_title = page_title.strip('/\t\n\r')			# - trim and remove slash from GET page_title param

			context_action = '/' + page_title					# - generate link to view page (shown on pg header)

			if page_title == "":								# - check if title is an empty string, if so assign
				page_title = HOME_PAGE_ID						#	ID of a home page
			
			page = Page.get_by_key_name(page_title)				# - querying page
			
			if page:											# if page exists, pass it's content to edit page
				self.render_front(content = page.content, 
					user = user, 
					context_action = context_action)
			else:												
				self.render_front(user = user, 
					context_action = '/' + context_action)
		else:													#if not logged in, redirect to login
			self.redirect('/login')

	def post(self, page_title = ""):
		"""
		Process a POST request from page edit.
    	
    	Args:
        page_title: Page title.
    
		"""

		page_title = page_title.strip('/\t\n\r')				#trim and remove slash from GET page_title param
		
		if page_title == "":									#Check if title is an empty string, if so assign
			page_title = HOME_PAGE_ID							#ID of a home page
		
		content = self.request.get("content")					#Get content param

		cont = Page(key_name = page_title, content = content)	#Init an entity variable
		cont.put()												#Insert to DB
			
		if page_title == HOME_PAGE_ID:							#redirect to view
			self.redirect('/')
		else:
			self.redirect('/'+page_title)

																#***Routing***
app = webapp2.WSGIApplication([('/signup',SignUp),				#User sign up
								('/login',Login),				#User log in
								('/logout',Logout),				#User log out
								('/_edit' + PAGE_RE, EditPage),	#Page editing
                               	(PAGE_RE, WikiPage),			#Page viewing
								], debug = True)
