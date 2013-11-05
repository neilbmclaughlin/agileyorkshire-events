from datetime import datetime
from google.appengine.ext import ndb

__author__ = 'neil'


class Event(ndb.Model):
    date = ndb.DateTimeProperty()
    title = ndb.StringProperty()
    description = ndb.StringProperty(indexed=False)
    capacity = ndb.IntegerProperty()
    image = ndb.BlobProperty()
    presentation_keys = ndb.KeyProperty(kind='Presentation', repeated=True)
    #presentations = ndb.ComputedProperty(lambda self: [p.get() for p in self.presentation_keys])

    @staticmethod
    def get_next_event_by_date():
        next_event = Event.query(Event.date >= datetime.now()).order(+Event.date).fetch(1)
        return next_event[0] if next_event else None


