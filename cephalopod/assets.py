from flask import current_app
from werkzeug.urls import url_parse


# view func
def versioned_static_file(version, filename):
    """Handles a static file with a versioned URL."""
    return current_app.send_static_file(filename)


# template filter
def version_url(value):
    """Moves the version tag from the query string to the URL"""
    url = url_parse(value)
    if not url.query:
        return value
    path = url.path.replace('/static', '/static_v/' + url.query, 1)
    return str(url.replace(path=path, query=''))
