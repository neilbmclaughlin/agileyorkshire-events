import os
import urllib
import datetime

from google.appengine.ext import ndb
import webapp2
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

def event_key(event_name):
    """Constructs a Datastore key for a Registration entity with event_date."""
    return ndb.Key('Event', event_name)


class Registration(ndb.Model):
    email_address = ndb.StringProperty(indexed=True)
    name = ndb.StringProperty(indexed=True)
    twitter_handle = ndb.StringProperty(indexed=True)
    date_registered = ndb.DateTimeProperty(auto_now_add=True)


class Event(ndb.Model):
    date = ndb.DateTimeProperty(indexed=True)
    description = ndb.StringProperty(indexed=True)

    @staticmethod
    def get_next_event_by_date():
        next_event = Event.query(Event.date >= datetime.datetime.now()).order(+Event.date).fetch(1)
        return next_event[0] if next_event else None


class Registrations(webapp2.RequestHandler):

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

        next_event = Event.get_next_event_by_date()

        if next_event:
            registrations = Registration.query(ancestor=next_event.key).fetch(100)

            template_values = {
                'registrations': registrations,
                'event': next_event,
            }

            template = JINJA_ENVIRONMENT.get_template('register.html')
            self.response.write(template.render(template_values))
        else:
            self.response.write('There is no next event setup')

    def post(self):
        next_event = Event.get_next_event_by_date()
        registration = Registration(parent=next_event.key)
        registration.email_address = self.request.get('email_address')
        registration.name= self.request.get('name')
        registration.twitter_handle = self.request.get('twitter_handle')
        registration.put()
        self.redirect('/register')


class Events(webapp2.RequestHandler):
    def get(self):
        nextEvent = Event.query(Event.date >= datetime.datetime.now()).order(+Event.date).fetch(1)
        events = Event.query(Event.date >= datetime.datetime.now()).order(-Event.date).fetch(100)
        template_values = {
           'events': events,
         }

        template = JINJA_ENVIRONMENT.get_template('events.html')
        self.response.write(template.render(template_values))
        
    def post(self):
        event = Event()
        event.date = datetime.datetime.strptime( self.request.get('event_date'), "%d %b %Y")
        event.description = self.request.get('event_description')
        event.put()
        self.redirect('/events')

application = webapp2.WSGIApplication([
    ('/registrations', Registrations),
    ('/events', Events),
    ('/register', Register),
], debug=True)
