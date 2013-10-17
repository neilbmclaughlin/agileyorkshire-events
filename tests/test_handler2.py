from webtest import TestApp
from event_manager import application

app = TestApp(application)

def test_registrationIncludesTwitterhandle():
    response = app.get('/registrations?event_name=20130101')
    assert '@neilbmclaughlin' in str(response)


