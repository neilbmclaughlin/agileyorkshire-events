import unittest
import webapp2

import event_manager  

class TestHandlers(unittest.TestCase):
   def test_hello(self):
       # Build a request object passing the URI path to be tested.
       # You can also pass headers, query arguments etc.
       request = webapp2.Request.blank('/registrations?event_name=20130101')
       # Get a response for that request.
       response = request.get_response(event_manager.application)

       # Let's check if the response is correct.
       self.assertEqual(response.status_int, 200)
       self.assertEqual(response.body, 'Hello t\'World!')
       self.assertEqual(len(response.headers), 3)

if __name__ == '__main__':
    unittest.main()
