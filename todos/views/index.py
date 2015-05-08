
import os
import hashlib
from pkg_resources import resource_filename

from todos.framework import View, Response

CSS_FILES = [
  'static/bower/todomvc-common/base.css',
  'static/bower/todomvc-app-css/index.css',
]

JS_FILES = [
  'static/bower/todomvc-common/base.js',
  'static/bower/react/react-with-addons.js',
  'static/bower/director/build/director.js',
  'static/bower/reconnectingWebsocket/reconnecting-websocket.min.js',
  'static/bower/superagent/superagent.js',
  'static/js/utils.js',
  'static/js/todoModel.js',
]

TMPL = """
<html>
  <head>
    <title>Realtime Python+Postgres TodoMVC</title>

    <!--style-->
    {css_files}
  </head>
  <body>
    <section id="todoapp" class="todoapp"></section>
    <footer id="info">
            <p>Double-click to edit a todo</p>
            <p>Created by <a href="http://github.com/petehunt/">petehunt</a></p>
            <p>Part of <a href="http://todomvc.com">TodoMVC</a></p>
    </footer>

    <!--libraries-->
    {js_files}
  </body>
</html>
"""

DEV_SCRIPTS = """
<!--UI-->
<script src="/static/bower/react/JSXTransformer.js" type="text/javascript" charset="utf-8" ></script>
<script src="/static/jsx/todoItem.jsx" type="text/jsx"></script>
<script src="/static/jsx/footer.jsx" type="text/jsx"></script>
<script src="/static/jsx/app.jsx" type="text/jsx"></script>
"""

# Use md5 sums for cache busting.
def hash_file(filename):
  filepath = resource_filename('todos', filename)
  with open(filepath) as f:
    data = f.read()
  return hashlib.md5(data).hexdigest()[:8]

def css_tag(filename):
  return '<link rel="stylesheet" href="/{filename}?{hash}" />'.format(filename=filename, hash=hash_file(filename))

def js_tag(filename):
  return '<script src="/{filename}?{hash}" type="text/javascript"></script>'.format(filename=filename, hash=hash_file(filename))

if os.path.isfile(resource_filename('todos', 'static/js/compiled.js')):
    JS_FILES.append('static/js/compiled.js')
    HOME = TMPL.format(js_files="\n".join(js_tag(s) for s in JS_FILES),
                       css_files="\n".join(css_tag(s) for s in CSS_FILES))
else:
    HOME = TMPL.format(js_files="\n".join(js_tag(s) for s in JS_FILES)+DEV_SCRIPTS,
                       css_files="\n".join(css_tag(s) for s in CSS_FILES))


class Index(View):
    def get(self):
        return Response(HOME, content_type='text/html; charset=utf-8')
