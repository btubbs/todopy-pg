import urlparse


def parse_pgurl(db_url):
    """
    Given a SQLAlchemy-compatible Postgres url, return a dict with
    keys for user, password, host, port, and database.
    """

    parsed = urlparse.urlsplit(db_url)
    return {
        'user': parsed.username,
        'password': parsed.password,
        'database': parsed.path.lstrip('/'),
        'host': parsed.hostname,
        'port': parsed.port,
    }


