/*jshint quotmark:false */
/*jshint white:false */
/*jshint trailing:false */
/*jshint newcap:false */
var app = app || {};

// polyfill Array.findIndex
if (!Array.prototype.findIndex) {
  Array.prototype.findIndex = function(predicate) {
    if (this == null) {
      throw new TypeError('Array.prototype.findIndex called on null or undefined');
    }
    if (typeof predicate !== 'function') {
      throw new TypeError('predicate must be a function');
    }
    var list = Object(this);
    var length = list.length >>> 0;
    var thisArg = arguments[1];
    var value;

    for (var i = 0; i < length; i++) {
      value = list[i];
      if (predicate.call(thisArg, value, i, list)) {
        return i;
      }
    }
    return -1;
  };
}

(function () {
	//'use strict';

  var WSPREFIX = function() {
    var loc = window.location, newUri;
    if (loc.protocol === "https:") {
        newUri = "wss:";
    } else {
        newUri = "ws:";
    }
    newUri += "//" + loc.host;
    return newUri;
  }();

	var Utils = app.Utils;
	// Generic "model" object. You can use whatever
	// framework you want. For this application it
	// may not even be worth separating this logic
	// out, but we do this to demonstrate one way to
	// separate out parts of your application.
	app.TodoModel = function (key) {
		this.key = key;
    this.todos = [];
		this.onChanges = [];

    this.ws = new ReconnectingWebSocket(WSPREFIX + '/api/todos/');
    this.ws.onmessage = app.TodoModel.prototype.onmessage.bind(this);
	};

  app.TodoModel.prototype.onmessage = function (ev) {
    // if todo is already in this.todos, then replace it
    // if not in, then add it.
    var todo = JSON.parse(ev.data);
    if (todo._op==='DELETE') {
      this.todos = this.todos.filter(function(t) {return t.id!==todo.id;});
    } else {
      var idx = this.todos.findIndex(function(t) {
        return t.id===todo.id;
      });

      if (idx==-1) {
        this.todos.push(todo);
      } else {
        this.todos[idx] = todo;
      }
    }
    this.inform();
  };

	app.TodoModel.prototype.subscribe = function (onChange) {
		this.onChanges.push(onChange);
	};

	app.TodoModel.prototype.inform = function () {
		Utils.store(this.key, this.todos);
		this.onChanges.forEach(function (cb) { cb(); });
	};

	app.TodoModel.prototype.addTodo = function (title) {
    superagent.post('/api/todos/').send({"title": title}).end();
	};

	app.TodoModel.prototype.toggleAll = function (checked) {
		this.todos.map(function (todo) {
      todo.completed = checked;
      superagent.put('/api/todos/' + todo.id + '/').send(todo).end();
		});
	};

	app.TodoModel.prototype.toggle = function (todoToToggle) {
    todoToToggle.completed = !todoToToggle.completed;
    superagent.put('/api/todos/' + todoToToggle.id + '/').send(todoToToggle).end();
	};

	app.TodoModel.prototype.destroy = function (todo) {
    superagent.del('/api/todos/' + todo.id + '/').end();
	};

	app.TodoModel.prototype.save = function (todoToSave, text) {
    todoToSave.title = text;
    superagent.put('/api/todos/' + todoToSave.id + '/').send(todoToSave).end();
	};

	app.TodoModel.prototype.clearCompleted = function () {
		this.todos.map(function (todo) {
      if (todo.completed) {
        app.TodoModel.prototype.destroy(todo);
      }
    });
	};

})();
