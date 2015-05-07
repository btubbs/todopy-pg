import json
import logging

from todos.framework import ApiView, JSONResponse


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TodoList(ApiView):

    def get_todos(self):
        self.db.execute("SELECT row_to_json(todos) FROM todos;")
        return self.db

    def get(self):
        return JSONResponse({
            'objects': [t[0] for t in self.get_todos()]
        })

    def websocket(self):
        for t in self.get_todos():
            self.ws.send(json.dumps(t[0]))

        self.bind_pg_to_websocket()


class TodoDetail(ApiView):

    def get(self, todo_id):
        return JSONResponse(self.get_todo(todo_id))

    def websocket(self, todo_id):
        t = self.get_todo(todo_id)
        self.ws.send(json.dumps(t))
        self.bind_pg_to_websocket(filter_id=todo_id)
