#!/usr/bin/env python

"""
A super simple migrations framework that uses raw .sql files and relies on
Postgres's transactional DDL feature for safety.

Each forward.sql migration file is expected to insert its name into a
migration_history table.
"""

import logging
from pkg_resources import resource_filename
import os
import sys
import urlparse

import psycopg2

from todos.utils import parse_pgurl


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def run(settings):
    conn = psycopg2.connect(**parse_pgurl(settings.db_url))
    conn.autocommit = True
    cur = conn.cursor()
    migrations_folder = resource_filename('todos', 'migrations')
    migration_names = [i for i in os.listdir(migrations_folder) if
                       os.path.isdir(os.path.join(migrations_folder, i))]

    logger.info('Found migrations: ' + ', '.join(migration_names))

    try:
        cur.execute('SELECT name FROM migration_history ORDER BY name;')
        completed_migrations = [m[0] for m in cur]
    except psycopg2.ProgrammingError:
        # The first migration creates the migration_history table.  So the query
        # on that table will fail if we have never run migrations.
        completed_migrations = []

    logger.info('Already run: ' + ', '.join(completed_migrations))

    to_run = sorted(list(set(migration_names).difference(completed_migrations)))

    if not len(to_run):
        logger.info('No migrations need running.')
        return
    logger.info('Migrations to run: ' + ', '.join(to_run))

    for m in to_run:
        logger.info('Running %s.' % m)
        script = os.path.join(migrations_folder, m, 'forward.sql')
        sql = open(script).read()
        cur.execute(sql)


def run_and_sleep(settings):
    run(settings)
    logger.info('Sleeping')
    sys.stdin.read()



if __name__ == '__main__':
    run()
