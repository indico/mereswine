from functools import wraps
from flask import g, url_for


# before request
def setup_breadcrumbs():
    """Initializes the breadcrumb navigation"""
    g.breadcrumbs = []


def menu(item):
    """Sets the active menu item for a view function."""

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            g.menu = item
            return f(*args, **kwargs)

        return wrapper

    return decorator


def breadcrumb(title, endpoint=None, **endpoint_args):
    """Creates a new static breadcrumb for a view function."""

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            g.breadcrumbs.append(make_breadcrumb(title, endpoint, **endpoint_args))
            return f(*args, **kwargs)

        return wrapper

    return decorator


def make_breadcrumb(title, endpoint=None, **endpoint_args):
    """Creates a new breadcrumb during view function execution."""
    return {'title': title,
            'link': url_for(endpoint, **endpoint_args) if endpoint else None}
