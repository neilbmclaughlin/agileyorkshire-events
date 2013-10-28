from google.appengine.ext import ndb

__author__ = 'neil'


class Registration(ndb.Model):
    email_address = ndb.StringProperty(indexed=True)
    name = ndb.StringProperty(indexed=True)
    twitter_handle = ndb.StringProperty(indexed=True)
    date_registered = ndb.DateTimeProperty(auto_now_add=True)
    confirmed = ndb.BooleanProperty()