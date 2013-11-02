from google.appengine.ext import ndb

__author__ = 'neil'


class Presentation(ndb.Model):
    name = ndb.StringProperty()
    outline = ndb.StringProperty(indexed=False)
    event_key = ndb.KeyProperty(kind='Event')

