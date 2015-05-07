import logging
import argparse
import os

from gunicorn.app.base import Application
from gunicorn import util
from todos.settings import get_settings
from todos import migrations


logging.basicConfig()

def main():
    # Extremely basic subcommand dispatcher.
    parser = argparse.ArgumentParser()

    commands = {
        'migrate': migrations.run,
        'migrate_and_sleep': migrations.run_and_sleep,
        'web': run_web,
    }

    cmd_help = "one of: %s" % ', '.join(sorted(commands.keys()))

    parser.add_argument('command', help=cmd_help, type=lambda x: commands.get(x))

    args = parser.parse_args()

    if args.command is None:
        raise SystemExit('Command must be ' + cmd_help)
    args.command(get_settings())


class TodoApplication(Application):
    """
    Wrapper around gunicorn so we can start app as "todos web" instead of a
    big ugly gunicorn line.
    """

    def __init__(self, settings):
        self.settings = settings
        super(TodoApplication, self).__init__()

    def init(self, *args):
        """
        Return todos-specific settings.
        """
        return {
            'bind': '0.0.0.0:%s' % os.getenv('PORT', 8000),
            'worker_class': 'gwebsocket.gunicorn.GWebSocketWorker',
            'timeout': self.settings.web_worker_timeout,
            'accesslog': '-',
        }

    def load(self):
        return util.import_app("todos:app")


def run_web(settings):
    from todos.green import patch
    patch()
    TodoApplication(settings).run()
