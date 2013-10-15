import cgi
import os
import urllib
import logging

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

def event_key(event_date):
    """Constructs a Datastore key for a Registration entity with event_date."""
    return ndb.Key('Event', event_date)


class Registration(ndb.Model):
    """Models an individual Registration entry with email and registration date."""
    email_address = ndb.StringProperty(indexed=True)
    name = ndb.StringProperty(indexed=True)
    twitter_handle = ndb.StringProperty(indexed=True)
    date_registered = ndb.DateTimeProperty(auto_now_add=True)


class MainPage(webapp2.RequestHandler):

    def get(self):
        event_name= self.request.get('event_name')

        if event_name:
            ancestor_key = event_key(event_name)
            registrations_query = Registration.query(ancestor=ancestor_key).order(Registration.name)
            registrations = registrations_query.fetch(100)

            template_values = {
                'registrations': registrations,
                'event_name': urllib.quote_plus(event_name),
            }

            template = JINJA_ENVIRONMENT.get_template('index.html')
            self.response.write(template.render(template_values))
        else:
            self.response.write('Event name not specified')


class Register(webapp2.RequestHandler):

    def get(self):
        event_name= "20130101"
        if event_name:
            ancestor_key = event_key(event_name)
            registrations_query = Registration.query(ancestor=ancestor_key).order(Registration.name)
            registrations = registrations_query.fetch(100)

            template_values = {
                'registrations': registrations,
                'event_name': urllib.quote_plus(event_name),
            }

            template = JINJA_ENVIRONMENT.get_template('register.html')
            self.response.write(template.render(template_values))
        else:
            self.response.write('Event name not specified')
        
    def post(self):
        event_name= "20130101"
        logging.debug(event_name)
        ancestor_key = event_key(event_name)
        registration = Registration(parent=ancestor_key)
        registration.email_address = self.request.get('email_address')
        registration.name= self.request.get('name')
        registration.twitter_handle = self.request.get('twitter_handle')
        registration.put()
        self.redirect('/register')


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/register', Register),
], debug=True)
