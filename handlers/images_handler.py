from google.appengine.ext import ndb
from handlers.base_handler import BaseRequestHandler


class ImagesHandler(BaseRequestHandler):
    def get(self):
        image_event_key = ndb.Key(urlsafe=self.request.get('k'))

        event = image_event_key.get()

        if event.image:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(event.image)
        else:
            self.response.out.write('No image')