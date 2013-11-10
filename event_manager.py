import os
import urllib
from datetime import datetime
from datetime import timedelta

from google.appengine.ext import ndb
from google.appengine.api import mail

import webapp2
import jinja2
from models.event import Event
from models.registration import Registration
from models.presentation import Presentation

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates'),
    extensions=['jinja2.ext.autoescape'])


DEFAULT_GROUP_NAME = 'AgileYorkshire'



def get_event_key(event_name):
    """Constructs a Datastore key for a Registration entity with event_date."""
    return ndb.Key('Event', event_name)


def get_group_key(group_name=DEFAULT_GROUP_NAME):
    return ndb.Key('Group', group_name)


class AdminHandler(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render())


class RegistrationsHandler(webapp2.RequestHandler):

    def get(self):
        event_name= self.request.get('event_name')

        if event_name:
            ancestor_key = get_event_key(event_name)
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


class RegistrationHandler(webapp2.RequestHandler):

    def get(self, registration_id):

        registration_key = ndb.Key(urlsafe=registration_id)
        registration = registration_key.get()

        confirm_link = self.url_for('confirm_registration', registration_id=registration_id)
        cancel_link = self.url_for('cancel_registration', registration_id=registration_id)

        print registration
        template_values = {
            'registration': registration,
            'confirm_link' : confirm_link,
            'cancel_link' : cancel_link,
        }

        template = JINJA_ENVIRONMENT.get_template('registration.html')
        self.response.write(template.render(template_values))


class NextEventHandler(webapp2.RequestHandler):

    def get(self):

        next_event = Event.get_next_event_by_date()

        if next_event:
            template_values = {
                'registrations_remaining': ( next_event.capacity - Registration.query(ancestor=next_event.key).count(next_event.capacity) ),
                'event': next_event,
            }

            template = JINJA_ENVIRONMENT.get_template('next_event.html')
            self.response.write(template.render(template_values))
        else:
            self.response.write('There is no next event setup')


class RegisterHandler(webapp2.RequestHandler):

    def get(self):

        next_event = Event.get_next_event_by_date()

        if next_event:

            registration_opens = next_event.date - timedelta(days=14)
            registration_open = datetime.now() > registration_opens

            presentations = Presentation.query(ancestor=get_group_key()).filter(Presentation.event_key == next_event.key).fetch(100)
            registrations = Registration.query(ancestor=next_event.key).fetch(100)

            template_values = {
                'registrations_remaining': ( next_event.capacity - Registration.query(ancestor=next_event.key).count(next_event.capacity) ),
                'registrations': registrations,
                'event': next_event,
                'presentations': presentations,
                'registration_open': registration_open,
                'registration_opens': registration_opens
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
        registration.confirmed = False
        key = registration.put()

        registration_url = self.url_for('registration', _full=True, registration_id=key.urlsafe())

        print registration_url

        mail.send_mail(
            'neil.mclaughlin@agileyorkshire.org',
            registration.email_address,
            'click link to confirm',
            registration_url)

        self.redirect('/register')


class ConfirmationHandler(webapp2.RequestHandler):

    def post(self, registration_id):

        registration_key = ndb.Key(urlsafe=registration_id)
        registration = registration_key.get()
        registration.confirmed = True
        registration.put()

        self.redirect('/register')


class CancellationHandler(webapp2.RequestHandler):

    def post(self, registration_id):

        registration_key = ndb.Key(urlsafe=registration_id)
        registration_key.delete()

        self.redirect('/register')


class EventsHandler(webapp2.RequestHandler):
    def get(self):
        events = Event.query(ancestor=get_group_key()).filter(Event.date >= datetime.now()).order(+Event.date).fetch(100)
        presentations = Presentation.query(ancestor=get_group_key()).filter(Presentation.event_key == None).fetch(100)
        template_values = {
            'events': events,
            'presentations': presentations
        }
        template = JINJA_ENVIRONMENT.get_template('events.html')
        self.response.write(template.render(template_values))
        
    def post(self):
        event = Event(parent=get_group_key())
        event.date = datetime.strptime( self.request.get('event_date'), "%d %b %Y")
        event.title = self.request.get('event_title')
        event.description = self.request.get('event_description')
        event.capacity = int(self.request.get('event_capacity'))
        event.registration_window = int(self.request.get('event_registration_window'))
        event_image = self.request.get('event_image')
        event.image = event_image
        presentations = self.request.get_all('event_presentations')

        event_key = event.put()

        for p in presentations:
            presentation_key = ndb.Key(urlsafe=p)
            presentation = presentation_key.get()
            presentation.event_key = event_key
            presentation.put()

        self.redirect('/events')


class PresentationEditHandler(webapp2.RequestHandler):

    def get(self, presentation_id):
        presentation = ndb.Key(urlsafe=presentation_id).get()
        post_link = self.url_for('edit_presentation', presentation_id=presentation_id)
        template_values = {
            'presentation': presentation,
            'post_link': post_link

        }
        template = JINJA_ENVIRONMENT.get_template('presentation_edit.html')
        self.response.write(template.render(template_values))

    def post(self, presentation_id):
        presentation = ndb.Key(urlsafe=presentation_id).get()
        presentation.name = self.request.get('presentation_name')
        presentation.outline = self.request.get('presentation_outline')
        presentation.put()
        self.redirect(self.url_for('presentations'))


class PresentationHandler(webapp2.RequestHandler):

    def get(self):
        presentations = Presentation.query(ancestor=get_group_key()).fetch(100)
        for presentation in presentations:
            presentation.edit_url = self.url_for('edit_presentation', presentation_id=presentation.key.urlsafe())

        template = JINJA_ENVIRONMENT.get_template('presentation.html')
        template_values = {
            'presentations': presentations,
            'post_url': self.url_for('presentations')
        }
        self.response.write(template.render(template_values))

    def post(self):
        presentation = Presentation(parent=get_group_key())
        presentation.name = self.request.get('presentation_name')
        presentation.outline = self.request.get('presentation_outline')
        presentation.put()
        self.redirect(self.url_for('presentations'))


class ImagesHandler(webapp2.RequestHandler):
    def get(self):
        image_event_key = ndb.Key(urlsafe=self.request.get('k'))

        event = image_event_key.get()

        if event.image:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(event.image)
        else:
            self.response.out.write('No image')

application = webapp2.WSGIApplication([
    ('/admin', AdminHandler),
    ('/registrations', RegistrationsHandler),
    webapp2.Route(r'/confirm_registration/<registration_id:[a-zA-Z0-9-_]+>', handler=ConfirmationHandler, name='confirm_registration'),
    webapp2.Route(r'/cancel_registration/<registration_id:[a-zA-Z0-9-_]+>', handler=CancellationHandler, name='cancel_registration'),
    ('/events/next', NextEventHandler),
    ('/events', EventsHandler),
    ('/register', RegisterHandler),
    webapp2.Route(r'/presentations/<presentation_id:[a-zA-Z0-9-_]+>', handler=PresentationEditHandler, name='edit_presentation'),
    webapp2.Route(r'/presentations', handler=PresentationHandler, name='presentations'),
    webapp2.Route(r'/registration/<registration_id:[a-zA-Z0-9-_]+>', handler=RegistrationHandler, name='registration'),
    ('/images', ImagesHandler),
], debug=True)


