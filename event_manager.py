import webapp2
from handlers.admin_handler import AdminHandler

from handlers.events_handler import EventsHandler
from handlers.images_handler import ImagesHandler
from handlers.presentation_handlers import PresentationEditHandler
from handlers.presentation_handlers import PresentationHandler
from handlers.registration_handlers import RegisterHandler
from handlers.registration_handlers import RegistrationHandler
from secrets import SESSION_KEY

app_config = {
    'webapp2_extras.sessions': {
        'cookie_name': '_simpleauth_sess',
        'secret_key': SESSION_KEY
    },
}

application = webapp2.WSGIApplication([
    ('/admin', AdminHandler),
    webapp2.Route(r'/confirm_registration/<registration_id:[a-zA-Z0-9-_]+>', handler=RegistrationHandler, name='confirm_registration', handler_method='confirm'),
    webapp2.Route(r'/cancel_registration/<registration_id:[a-zA-Z0-9-_]+>', handler=RegistrationHandler, name='cancel_registration', handler_method='cancel'),
    #('/events/next', NextEventHandler),
    ('/events', EventsHandler),
    ('/register', RegisterHandler),
    webapp2.Route(r'/presentations/<presentation_id:[a-zA-Z0-9-_]+>', handler=PresentationEditHandler, name='edit_presentation'),
    webapp2.Route(r'/presentations', handler=PresentationHandler, name='presentations'),
    webapp2.Route(r'/registration/<registration_id:[a-zA-Z0-9-_]+>', handler=RegistrationHandler, name='registration'),
    webapp2.Route(r'/registrations', handler=RegistrationHandler, name='registrations', handler_method='index'),
    ('/images', ImagesHandler),
], debug=True, config=app_config)


