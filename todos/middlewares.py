

class DummyAuthMiddleware(object):

    def __init__(self, app, config):
        self.app = app
        self.username = config['username']

    def __call__(self, environ, start_response):
        environ['beaker.session']['username'] = self.username
        return self.app(environ, start_response)
