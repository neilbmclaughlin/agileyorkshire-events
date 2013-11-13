import urllib

from datetime import timedelta, datetime
from google.appengine.api import mail
from models.event import Event
from models.presentation import Presentation
from models.registration import Registration
from handlers.base_handler import BaseRequestHandler
from google.appengine.ext import ndb


class RegisterHandler(BaseRequestHandler):

    def get(self):

        next_event = Event.get_next_event_by_date()

        if next_event:

            registration_opens = next_event.date - timedelta(days=14)
            registration_open = datetime.now() > registration_opens

            presentations = Presentation.query(ancestor=self.get_group_key()).filter(Presentation.event_key == next_event.key).fetch(100)
            registrations = Registration.query(ancestor=next_event.key).fetch(100)

            template_values = {
                'registrations_remaining': ( next_event.capacity - Registration.query(ancestor=next_event.key).count(next_event.capacity) ),
                'registrations': registrations,
                'event': next_event,
                'presentations': presentations,
                'registration_open': registration_open,
                'registration_opens': registration_opens
            }
            self.render('register.html', template_values)
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


class RegistrationHandler(BaseRequestHandler):

    def index(self):
        next_event = Event.get_next_event_by_date()

        if next_event:
            ancestor_key = next_event.key
            registrations_query = Registration.query(ancestor=ancestor_key).order(Registration.name)
            registrations = registrations_query.fetch(100)

            template_values = {
                'registrations': registrations,
                'event_name': urllib.quote_plus(next_event.title),
            }

            self.render('registrations.html', template_values)
        else:
            self.response.write('Event name not specified')

    def get(self, registration_id):

        registration_key = ndb.Key(urlsafe=registration_id)
        registration = registration_key.get()

        confirm_link = self.url_for('confirm_registration', registration_id=registration_id)
        cancel_link = self.url_for('cancel_registration', registration_id=registration_id)

        print registration
        template_values = {
            'registration': registration,
            'confirm_link': confirm_link,
            'cancel_link': cancel_link,
        }

        self.render('registration.html', template_values)

    def confirm(self, registration_id):

        registration_key = ndb.Key(urlsafe=registration_id)
        registration = registration_key.get()
        registration.confirmed = True
        registration.put()

        self.redirect('/register')

    def cancel(self, registration_id):

        registration_key = ndb.Key(urlsafe=registration_id)
        registration_key.delete()

        self.redirect('/register')


