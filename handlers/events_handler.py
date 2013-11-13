from datetime import datetime
from google.appengine.ext import ndb
from models.event import Event
from models.presentation import Presentation
from handlers.base_handler import BaseRequestHandler


class EventsHandler(BaseRequestHandler):
    def get(self):
        events = Event.query(ancestor=self.get_group_key()).filter(Event.date >= datetime.now()).order(+Event.date).fetch(100)
        presentations = Presentation.query(ancestor=self.get_group_key()).filter(Presentation.event_key == None).fetch(100)
        template_values = {
            'events': events,
            'presentations': presentations
        }
        self.render('events.html', template_values)

    def post(self):
        event = Event(parent=self.get_group_key())
        event.date = datetime.strptime(self.request.get('event_date'), "%d %b %Y")
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