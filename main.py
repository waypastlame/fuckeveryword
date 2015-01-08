# Copyright (c) Brendan McCarthy

import os
import webapp2
import ConfigParser
import jinja2
import string
import tweepy
import logging
import urllib
import re
import sys

from tweepy import *
from google.appengine.api import users
from google.appengine.ext import db

JINJA_ENVIRONMENT = jinja2.Environment(
	loader     = jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions = ['jinja2.ext.autoescape'],
	autoescape = False)

class Index(db.Model):
	index = db.IntegerProperty()

def tweet(status):
	config = ConfigParser.RawConfigParser()
	config.read('settings.cfg')
	
	# http://dev.twitter.com/apps/myappid
	CONSUMER_KEY = config.get('API Information', 'CONSUMER_KEY')
	CONSUMER_SECRET = config.get('API Information', 'CONSUMER_SECRET')
	# http://dev.twitter.com/apps/myappid/my_token
	ACCESS_TOKEN_KEY = config.get('API Information', 'ACCESS_TOKEN_KEY')
	ACCESS_TOKEN_SECRET = config.get('API Information', 'ACCESS_TOKEN_SECRET')

	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
	auth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
	api = tweepy.API(auth)
	result = api.update_status(status)

def get_current_line(index):
	with open("words.txt") as source_fh:
		for i in range(index+1):
			status_str = "fuck " + source_fh.readline().strip()
		return status_str

class MainHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		disabled = ""

		if users.get_current_user():
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Hello, ' + user.nickname() + '. Logout'
			if user.nickname() == "brendan10211" or user.nickname() == "test@example.com":
				disabled = ""
			else:
				disabled = "disabled"
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Hello, guest. Login'
			disabled = "disabled"

		template_values = {
			'url': url,
			'url_linktext': url_linktext,
			'disabled': disabled,
		}

		template = JINJA_ENVIRONMENT.get_template('index.html')
		self.response.write(template.render(template_values))

class TweetHandler(webapp2.RequestHandler):
	def get(self):
		indexList = db.GqlQuery("SELECT * " +
    							"FROM Index ")
		indexNum = indexList[0].index
		tweet_text = get_current_line(indexNum)

		try:
			tweet(tweet_text)
			logging.info(tweet_text)
		except TweepError as e: 
			logging.info(e)

		indexNum += 1

		db.delete(db.Query())

		newIndex = Index()
		newIndex.index = indexNum
		newIndex.put()

		self.redirect('/')

class MakeHandler(webapp2.RequestHandler):
	def get(self):
		index = Index()
		index.index = 0
		index.put()

		self.redirect('/')

class TestHandler(webapp2.RequestHandler):
	def get(self):
		tweet('fuck test')

		self.redirect('/')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/tweet', TweetHandler),
    ('/make', MakeHandler),
    ('/test', TestHandler),
], debug=True)
