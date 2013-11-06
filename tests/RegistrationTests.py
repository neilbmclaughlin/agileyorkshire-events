import unittest
from webtest import TestApp
from google.appengine.ext import testbed

from event_manager import application
from models.event import Event
from models.registration import Registration
from freezegun import freeze_time
from datetime import datetime
from datetime import timedelta
from freezegun import api
from google.appengine.api import datastore_types
from google.appengine.ext import db, ndb
import pytz


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

        # From: https://github.com/spulec/freezegun/issues/22

        # datetime.utcnow() needs to stay naive.
        if not hasattr(api.FakeDatetime, '_old_utcnow'):
          @classmethod
          def naive_utcnow(cls):
            return cls._old_utcnow().replace(tzinfo=None)

          api.FakeDatetime._old_utcnow = api.FakeDatetime.utcnow
          api.FakeDatetime.utcnow = naive_utcnow

        # ext.db.DateProperty.now() should return a FakeDate.
        @staticmethod
        def today():
          return api.date_to_fakedate(api.real_datetime.now().date())
        db.DateProperty.now = today

        # ext.ndb.DatetimeProperty.now() should return a naive FakeDatetime.
        def now(self):
          now = datetime.now()
          if now.tzinfo:
            now = now.astimezone(pytz.utc).replace(tzinfo=None)
          return api.datetime_to_fakedatetime(now)
        ndb.DateTimeProperty._now = now

        # Validating FakeDatetime's should work as expected.
        def validate_fakedatetime(name, value):
          return api.datetime_to_fakedatetime(value)

        # De-serializing a FakeDatetime should be the same as a regular datetime.
        def load_datetime(value):
          loaded_value = datastore_types._When(value)
          if issubclass(datetime, api.FakeDatetime):
            loaded_value = api.datetime_to_fakedatetime(loaded_value)
          return loaded_value

        # Tell App Engine how to handle FakeDatetime objects.
        datastore_types._VALIDATE_PROPERTY_VALUES[api.FakeDatetime] = validate_fakedatetime
        datastore_types._PACK_PROPERTY_VALUES[api.FakeDatetime] = datastore_types.PackDatetime
        datastore_types._PROPERTY_MEANINGS[api.FakeDatetime] = datastore_types.entity_pb.Property.GD_WHEN
        datastore_types._PROPERTY_CONVERSIONS[datastore_types.entity_pb.Property.GD_WHEN] = load_datetime


    def tearDown(self):            
        self.testbed.deactivate()

    def create_event(self, capacity=20, event_date=datetime.now() + timedelta(days=5), registration_window=5):
        event = Event(parent=ndb.Key('Group', 'AgileYorkshire'))
        event.date = event_date
        event.description = 'An event'
        event.capacity = capacity
        event.registration_window = registration_window
        event.put()
        return event

    def create_registrant(self, event, name):
        participant = Registration(parent=event.key)
        participant.name = name
        participant.email_address = name + '@home.com'
        participant.twitter_handle = '@' + name
        participant.put()
        return participant

    def test_FetchRegisterURL(self):
        self.create_event(capacity=20)

        result = self.testapp.get("/register")

        print result

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

    def test_PostingARegistrationShouldSendAConfirmationEmailWithLink(self):

        #Arrange
        self.create_event(capacity=20)
        self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

        form = self.testapp.get("/register").form
        form['email_address'] = 'bob@home.com'
        form['name'] = 'Bob Smith'
        form['twitter_handle'] = '@bob'

        #Act
        response = form.submit().follow()

        #Assert
        registration = Registration.query().fetch(1)[0];
        messages = self.mail_stub.get_sent_messages(to='bob@home.com')
        self.assertEqual(1, len(messages))
        self.assertEqual('neil.mclaughlin@agileyorkshire.org', messages[0].sender)
        self.assertTrue('/registration/' + registration.key.urlsafe() in messages[0].body.payload, 'email should contain a link to the registration')

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

    @freeze_time("2012-01-01")
    def test_WhenTheDateIsBeforeTheRegistrationStartDateOfTheNextEventThenItShouldNotBePossibleToRegister(self):

        #Arrange
        event = self.create_event(registration_window=14)
        event.date = datetime(2013, 3, 12, 18, 30)

        #Act
        response = self.testapp.get("/register")

        #Assert
        self.assertEqual(response.status, "200 OK")
        assert 'form' not in response

        assert 'Registration opens 26 Feb 2013 18:30' in response

    def test_ViewRegistrationDetails(self):

        #Arrange
        event = self.create_event(capacity=3)
        p1 = self.create_registrant(event, 'fred')

        #Act
        response = self.testapp.get("/registration/" + p1.key.urlsafe())

        #Assert
        self.assertEqual(response.status, "200 OK")

        assert 'fred' in response
        assert '@fred' in response
        assert 'fred@home.com' in response
        assert 'Confirm' in response

    @freeze_time("2012-01-01")
    def test_ConfirmRegistration(self):

        #Arrange
        event = self.create_event(capacity=3)
        p1 = self.create_registrant(event, 'bob')
        p2 = self.create_registrant(event, 'bill')
        p3 = self.create_registrant(event, 'fred')

        #Act
        response = self.testapp.post("/confirm_registration/" + p3.key.urlsafe()).follow()

        #Assert
        self.assertEqual(response.status, "200 OK")
        assert 'bob' in response
        assert 'bill' in response
        assert 'fred' in response

    @freeze_time("2012-01-01")
    def test_CancelRegistration(self):

        #Arrange
        event = self.create_event(capacity=3)
        p1 = self.create_registrant(event, 'bob')
        p2 = self.create_registrant(event, 'bill')
        p3 = self.create_registrant(event, 'fred')

        #Act
        response = self.testapp.post("/cancel_registration/" + p3.key.urlsafe()).follow()

        #Assert
        self.assertEqual(response.status, "200 OK")
        assert 'bob' in response
        assert 'bill' in response
        assert 'fred' not in response
