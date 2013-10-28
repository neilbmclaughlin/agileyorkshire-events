import unittest
from google.appengine.ext import ndb
from google.appengine.ext import testbed

from datetime import datetime

from event_manager import application
from models.event import Event


class EventHandlerTests(unittest.TestCase):

    def setUp(self):

        self.testbed = testbed.Testbed()

        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.setup_env(app_id='agileyorkshire_events')
        self.testbed.activate()

        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()

        # create a test server for us to prod
        # self.testapp = TestApp(application)

    def tearDown(self):
        self.testbed.deactivate()

    def testInsertEvent(self):
        event = Event(parent=ndb.Key('Group', 'Agile'))
        event.date = datetime.now()
        event.description = 'An event'
        event.capacity = 20
        event.put()
        self.assertEqual(1, len(Event.query().fetch(2)))

