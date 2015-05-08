from todos.green import patch; patch()

import os

from werkzeug.wsgi import SharedDataMiddleware

from todos.framework import App



from todos.settings import get_settings
from todos.views import index, api


routes = [
    ('/', 'index', index.Index),
    ('/api/todos/', 'todo_list', api.TodoList),
    ('/api/todos/<todo_id>/', 'todo_detail', api.TodoDetail),
]


def import_class(path):
    try:
        module, dot, klass = path.rpartition('.')
        imported = __import__(module, globals(), locals(), [klass, ], -1)
        return getattr(imported, klass)
    except Exception, e:
        raise ImportError(e)


if 'app' not in globals():
    settings = get_settings()
    app = App(routes, settings)
    #app.db = scoped_session(make_session_cls(settings.db_url))
    app = SharedDataMiddleware(app, {
        '/static': ('todos', 'static')
    })

    # also wrap the app in each middleware specified in settings.
    for cls_string, config in settings.wsgi_middlewares:
        cls = import_class(cls_string)
        app = cls(app, config)

if __name__ == "__main__":
    from gevent import pywsgi
    from gwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', int(os.getenv('PORT', 8000))), app,
                               handler_class=WebSocketHandler)
    server.serve_forever()

