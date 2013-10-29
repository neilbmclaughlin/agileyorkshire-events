import datetime
from google.appengine.ext import ndb

__author__ = 'neil'


class Event(ndb.Model):
    date = ndb.DateTimeProperty()
    title = ndb.StringProperty()
    description = ndb.StringProperty(indexed=False)
    capacity = ndb.IntegerProperty()
    image = ndb.BlobProperty()

    @staticmethod
    def get_next_event_by_date():
        next_event = Event.query(Event.date >= datetime.datetime.now()).order(+Event.date).fetch(1)
        return next_event[0] if next_event else None