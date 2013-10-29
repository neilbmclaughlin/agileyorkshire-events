import unittest
from webtest import TestApp
from google.appengine.ext import ndb
from google.appengine.ext import testbed

from event_manager import application
from models.event import Event
from models.registration import Registration

import datetime


class RegistrationTests(unittest.TestCase):

    #http://webtest.pythonpaste.org/en/latest/api.html#module-webtest

    #Note: had to edit File "/Library/Python/2.7/site-packages/WebTest-2.0.9-py2.7.egg/webtest/response.py", line 426, in html
    #soup = BeautifulSoup(self.testbody, "html.parser") << "xml" after installing lxml to prevent parsing error

    def setUp(self):

        self.testbed = testbed.Testbed()

        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.setup_env(app_id='agileyorkshire_events')
        self.testbed.activate()

        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_mail_stub()

        # create a test server for us to prod
        self.testapp = TestApp(application)

    def tearDown(self):            
        self.testbed.deactivate()

    def create_event(self, capacity):
        event = Event(parent=ndb.Key('Group', 'AgileYorkshire'))
        event.date = datetime.datetime.now() + datetime.timedelta(days=1)
        event.description = 'An event'
        event.capacity = capacity
        event.put()
        return event

    def create_registrant(self, event, name):
        participant = Registration(parent=event.key)
        participant.name = name
        participant.email_address = name + '@home.com'
        participant.put()
        return participant

    def testFetchRegisterURL(self):
        self.create_event(capacity=20)

        result = self.testapp.get("/register")
        self.assertEqual(result.status, "200 OK")
        assert 'Register here for the next event' in result
        assert 'There are 20 places remaining' in result


    def test_PostingARegistrationShouldAddToListUpdatePlacesRemainingCount(self):

        #Arrange
        self.create_event(capacity=20)

        form = self.testapp.get("/register").form
        form['email_address'] = 'bob@home.com'
        form['name'] = 'Bob Smith'
        form['twitter_handle'] = '@bob'

        #Act
        response = form.submit().follow()

        #Assert
        assert '@bob' in response
        assert 'There are 19 places remaining' in response

    def test_PostingARegistrationShouldSendAConfirmationEmail(self):

        #Arrange
        self.create_event()
        self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

        form = self.testapp.get("/register").form
        form['email_address'] = 'bob@home.com'
        form['name'] = 'Bob Smith'
        form['twitter_handle'] = '@bob'

        #Act
        response = form.submit().follow()

        #Assert
        messages = self.mail_stub.get_sent_messages(to='bob@home.com')
        self.assertEqual(1, len(messages))
        self.assertEqual('neil.mclaughlin@agileyorkshire.org', messages[0].sender)


    def test_WhenEventIsAtCapacityItShouldNotBePossibleToRegister(self):

        #Arrange
        event = self.create_event(capacity=3)
        p1 = self.create_registrant(event, 'bob')
        p2 = self.create_registrant(event, 'bill')
        p3 = self.create_registrant(event, 'fred')

        #Act
        response = self.testapp.get("/register")

        #Assert
        self.assertEqual(response.status, "200 OK")
        assert 'form' not in response
        assert 'There are 0 places remaining' in response
