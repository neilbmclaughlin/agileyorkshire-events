from handlers.base_handler import BaseRequestHandler


class AdminHandler(BaseRequestHandler):

    def get(self):
        self.render('index.html')
