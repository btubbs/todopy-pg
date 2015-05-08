import json
import logging

from werkzeug.utils import redirect
from werkzeug.exceptions import NotFound
from psycopg2 import ProgrammingError

from todos.framework import ApiView, JSONResponse, Response, reverse


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TodoList(ApiView):

    def get_todos(self):
        self.db.execute("SELECT row_to_json(todos) FROM todos ORDER BY created_time;")
        return self.db

    def get(self):
        return JSONResponse({
            'objects': [t[0] for t in self.get_todos()]
        })

    def post(self):
        title = json.loads(self.request.data)['title']
        self.db.execute("INSERT INTO todos (title) VALUES (%s) RETURNING id", (title,))
        uuid = self.db.fetchone()[0]
        url = reverse(self.app.map, 'todo_detail', {'todo_id': uuid})
        return redirect(url)

    def websocket(self):
        for t in self.get_todos():
            self.ws.send(json.dumps(t[0]))

        self.bind_pg_to_websocket()


class TodoDetail(ApiView):

    def get(self, todo_id):
        return JSONResponse(self.get_todo(todo_id))

    def put(self, todo_id):
        todo = json.loads(self.request.data)
        self.db.execute("UPDATE todos SET title=%s, completed=%s WHERE id=%s;", (
            todo['title'],
            todo['completed'],
            todo_id))
        url = reverse(self.app.map, 'todo_detail', {'todo_id': todo_id})
        return Response()

    def delete(self, todo_id):
        self.db.execute("DELETE FROM todos WHERE id=%s RETURNING id;",
                        (todo_id,))
        try:
            deleted = self.db.fetchone()[0]
        except ProgrammingError:
            return NotFound()

        return Response()


    def websocket(self, todo_id):
        t = self.get_todo(todo_id)
        self.ws.send(json.dumps(t))
        self.bind_pg_to_websocket(filter_id=todo_id)
