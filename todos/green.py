from gevent.monkey import patch_all
from gevent.local import local
from psycogreen.gevent import patch_psycopg


def patch():
    # Patch all the things that gevent knows about.
    patch_all()

    # Patch psycopg2 to also be gevent friendly.
    patch_psycopg()
