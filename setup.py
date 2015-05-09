#!/usr/bin/python

import setuptools

setup_params = dict(
    name='todos',
    version='0.0.3',
    author='Brent Tubbs',
    author_email='brent.tubbs@gmail.com',
    packages=setuptools.find_packages(),
    include_package_data=True,

    # Dependency versions are intentionally pinned to prevent surprises at
    # deploy time.  The world is not yet safely semver.
    install_requires=[
        'beaker==1.6.4',
        'gevent==1.0.1',
        'gwebsocket==0.9.6',
        'gunicorn==19.1.1',
        'psycogreen==1.0',
        'psycopg2==2.5.4',
        'PyYAML==3.11',
        'utc==0.0.3',
        'Werkzeug==0.10.1',
    ],
    entry_points={
        'console_scripts': [
            'todos = todos.cli:main',
        ]
    },
    description=('The TodoMVC app, synced between browsers in real time, on '
                 'top of Postgres and Python.'),
)

if __name__ == '__main__':
    setuptools.setup(**setup_params)
