from webapp2_extras import sessions
from google.appengine.ext import ndb
from handlers.base_handler import BaseRequestHandler
from models.presentation import Presentation


class PresentationHandler(BaseRequestHandler):

    def get(self):

        #https://simpleauth.appspot.com/

        session_store = sessions.get_store(request=self.request)
        flashes = session_store.get_session().get_flashes()

        presentations = Presentation.query(ancestor=self.get_group_key()).fetch(100)
        for presentation in presentations:
            presentation.edit_url = self.url_for('edit_presentation', presentation_id=presentation.key.urlsafe())

        template_values = {
            'flashes': flashes,
            'presentations': presentations,
            'post_url': self.url_for('presentations')
        }
        self.render('presentation.html', template_values)

    def post(self):
        presentation = Presentation(parent=self.get_group_key())
        presentation.name = self.request.get('presentation_name')
        presentation.outline = self.request.get('presentation_outline')
        presentation.put()
        session_store = sessions.get_store(request=self.request)
        session_store.get_session().add_flash('Presentation Created', level='alert')
        self.redirect(self.url_for('presentations'))


class PresentationEditHandler(BaseRequestHandler):

    def get(self, presentation_id):
        presentation = ndb.Key(urlsafe=presentation_id).get()
        post_link = self.url_for('edit_presentation', presentation_id=presentation_id)
        template_values = {
            'presentation': presentation,
            'post_link': post_link

        }
        self.render('presentation_edit.html', template_values)

    def post(self, presentation_id):
        presentation = ndb.Key(urlsafe=presentation_id).get()
        presentation.name = self.request.get('presentation_name')
        presentation.outline = self.request.get('presentation_outline')
        presentation.put()
        self.redirect(self.url_for('presentations'))