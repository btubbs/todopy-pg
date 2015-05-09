"""
The settings module for the app.

To add a new setting, set a default/in-development value for it in the DEFAULTS
dict below.

To override a default setting in production, write it to a YAML file and set the
file's path as the APP_SETTINGS_YAML environment variable.
"""
import os
import random
import string

import yaml

def random_secret(n=64):
    """
    Generate a random key to use for signing sessions.  This is only useful for
    dev mode.  If you try to use this in production, then sessions will be
    invalidated every time the server restarts, and if you load balance between
    multiple processes, each will think the other's sessions are invalid.
    """
    chars = string.ascii_letters + string.digits
    return ''.join([random.choice(chars) for x in xrange(n)])


DEFAULTS = {
    # use Heroku Postgres if present.
    'db_url': os.getenv('DATABASE_URL',
                        'postgresql://postgres@/todos'),
    'web_worker_timeout': 30,
    'websocket_ping_interval': 5,

    # a list of wsgi middleware classes that should be used to wrap the app, and
    # their config dicts.

    # Middlewares will be instantiated in order, so the last one wraps the
    # second-to-last one, etc.  This means that at request time, they're
    # executed in reverse order.

    # YOU MUST override this setting in production to provide your own session
    # key.
    'wsgi_middlewares': [
        ('todos.middlewares.DummyAuthMiddleware', {
            'username': 'test_user',
        }),
        ('beaker.middleware.SessionMiddleware', {
            'session.type': 'cookie',
            'session.cookie_expires': True,
            'session.key': 'session', # Name of the cookie we'll set.
            'session.validate_key': random_secret(),
            'session.auto': True,
            # allow running locally without https
            'session.secure': False,
        }),
    ]
}


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def get_settings():
    settings = AttrDict()
    settings.update(DEFAULTS)
    if 'APP_SETTINGS_YAML' in os.environ:
        with open(os.environ['APP_SETTINGS_YAML']) as f:
            settings.update(yaml.safe_load(f.read()))
    return settings
