import os
from jinja2 import TemplateNotFound
import webapp2
from webapp2_extras import sessions, jinja2
from google.appengine.ext import ndb


class BaseRequestHandler(webapp2.RequestHandler):

    DEFAULT_GROUP_NAME = 'AgileYorkshire'

    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    def get_template(self, template_name):
        self.jinja_environment().get_template(template_name)

    def jinja_environment(self):
        """Returns a Jinja2 renderer cached in the app registry"""
        return jinja2.jinja2.Environment(
            loader=jinja2.jinja2.FileSystemLoader(os.path.dirname(__file__) + '/../templates'),
            extensions=['jinja2.ext.autoescape'])

    @webapp2.cached_property
    def jinja2(self):
        """Returns a Jinja2 renderer cached in the app registry"""
        return jinja2.get_jinja2(app=self.app)

    def get_event_key(self, event_name):
        """Constructs a Datastore key for a Registration entity with event_date."""
        return ndb.Key('Event', event_name)

    def get_group_key(self, group_name=DEFAULT_GROUP_NAME):
        return ndb.Key('Group', group_name)

    @webapp2.cached_property
    def session(self):
        """Returns a session using the default cookie key"""
        return self.session_store.get_session()

    def render(self, template_name, template_vars={}):
        # Preset values for the template
        values = {
            'url_for': self.uri_for,
            'flashes': self.session.get_flashes()
        }

        # Add manually supplied template values
        values.update(template_vars)

        # read the template or 404.html
        try:
            self.response.write(self.jinja2.render_template(template_name, **values))
        except TemplateNotFound:
            self.abort(404)