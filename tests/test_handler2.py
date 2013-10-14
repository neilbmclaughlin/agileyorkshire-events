from webtest import TestApp
from helloworld import application

app = TestApp(application)

def test_index():
    response = app.get('/')
    assert 'Hello t\'World!' in str(response)
