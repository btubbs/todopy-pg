# -*- coding: utf-8 -*-
import json
import logging
import select

import gevent
import psycopg2
import utc
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import BaseRequest, BaseResponse
from werkzeug.exceptions import (HTTPException, MethodNotAllowed,
                                 NotImplemented, NotFound)
from gwebsocket.exceptions import SocketDeadError

from todos.utils import parse_pgurl

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Request(BaseRequest):
    """Encapsulates a request."""


class Response(BaseResponse):
    """Encapsulates a response."""


class JSONResponse(Response):
    def __init__(self, data, *args, **kwargs):
        kwargs['content_type'] = 'application/json'
        return super(JSONResponse, self).__init__(json.dumps(data), *args, **kwargs)


class View(object):
    """Baseclass for our views."""

    allowed_methods = ('GET', 'HEAD', 'POST', 'DELETE', 'PUT')

    def __init__(self, app, req, params):
        self.app = app
        self.request = req
        self.params = params

    def get(self):
        raise MethodNotAllowed()
    post = delete = put = get

    def head(self):
        return self.get()

    def cleanup(self):
        pass

    def __call__(self, environ, start_response):
        if self.request.method not in self.allowed_methods:
            raise NotImplemented()

        if self.request.method == 'GET' and 'wsgi.websocket' in environ:
            self.ws = environ['wsgi.websocket']
            self.ws.add_close_callback(self.cleanup)

            handler = self.websocket
        else:
            handler = getattr(self, self.request.method.lower())

        resp = handler(**self.params)
        return resp(environ, start_response)


class ApiView(View):
    def __init__(self, *args, **kwargs):
        super(ApiView, self).__init__(*args, **kwargs)
        self.dbconn = psycopg2.connect(**parse_pgurl(self.app.settings.db_url))
        self.dbconn.autocommit = True
        self.db = self.dbconn.cursor()

    def bind_pg_to_websocket(self, filter_id=None):
        self.db.execute('LISTEN todos_updates;')
        last_ping = utc.now()
        while True:
            # Handle sending keepalives on the socket.
            now = utc.now()
            elapsed = (now - last_ping).total_seconds()
            if elapsed > self.app.settings.websocket_ping_interval:
                self.ws.send_frame('', self.ws.OPCODE_PING)
                last_ping = now

            # Block on notifications from Postgres, with 5 sec timeout.
            if select.select([self.dbconn], [], [], 5) == ([], [], []):
                logger.debug("No messages for 5 seconds.")
            else:
                self.dbconn.poll()
                while self.dbconn.notifies:
                    notify = self.dbconn.notifies.pop()
                    payload = json.loads(notify.payload)
                    if filter_id is None or payload['id'] == filter_id:
                        # Handle payloads too big for a PG NOTIFY.
                        if 'error' in payload and 'id' in payload:
                            payload = self.get_todo(payload['id'])

                        self.ws.send(json.dumps(payload))

    def get_todo(self, todo_id):
        self.db.execute("SELECT row_to_json(todos) FROM todos WHERE id=%s", (todo_id,))
        return self.db.fetchone()[0]



class App(object):
    def __init__(self, urls, settings):
        self.urls = urls
        self.settings = settings
        self.map, self.handlers = build_rules(urls)

    def __call__(self, environ, start_response):
        try:
            req = Request(environ)
            try:
                # convenient access to Beaker session.  Will raise KeyError if
                # Beaker middleware is not enabled.
                req.session = environ['beaker.session']
                adapter = self.map.bind_to_environ(environ)
                view_name, params = adapter.match()
                view_cls = self.handlers[view_name]
                wsgi_app = view_cls(self, req, params)
            except HTTPException, e:
                wsgi_app = e
            resp = wsgi_app(environ, start_response)

            return resp
        finally:
            if 'wsgi_app' in locals() and hasattr(wsgi_app, 'dbconn'):
                logger.debug("Closing PG connection")
                wsgi_app.dbconn.close()


def build_rules(rules_tuples):
    """
    Given a list of tuples like this:

    [
        ('/', 'index', views.Index),
        ('/hello/<name>/', 'hello', views.Hello),
    ]

    Return two things:
        1. A Werkzeug Map object.
        2. A dictionary mapping the names of the Werkzeug endpoints to view
        classes.
    """
    handlers = {}
    rules = []
    for pat, name, view in rules_tuples:
        rules.append(Rule(pat, endpoint=name))
        handlers[name] = view
    return Map(rules), handlers


def reverse(rule_map, endpoint, values=None):
    """ Given a rule map, and the name of one of our endpoints, and a dict of
    parameter values, return a URL"""
    adapter = rule_map.bind('')
    return adapter.build(endpoint, values=values)
