import unittest
from webtest import TestApp
from google.appengine.ext import ndb
from google.appengine.ext import testbed

from event_manager import application

class MyFirstTest(unittest.TestCase):

    def setUp(self):

        self.testbed = testbed.Testbed()

        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.setup_env(app_id='agileyorkshire_events')
        self.testbed.activate()

        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()

        # create a test server for us to prod
        self.testapp = TestApp(application)

    def tearDown(self):            
        self.testbed.deactivate()

    def testFetchEventURL(self):

        result = self.testapp.get("/events")
        self.assertEqual(result.status, "200 OK")
        assert 'Agile Yorkshire Meetups' in result

    def testFetchRegisterURL(self):

        result = self.testapp.get("/register")
        self.assertEqual(result.status, "200 OK")
        print result
        assert 'Register here for the next event' in result
