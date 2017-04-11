from flask.ext.assets import Environment
from flask.ext.babel import Babel
from flask.ext.script import Manager
from flask.ext.sqlalchemy import SQLAlchemy
from flask_multipass import Multipass


# Flask extensions
assets = Environment()
db = SQLAlchemy()
babel = Babel()
multipass = Multipass()


class ContextfulManager(Manager):
    """Flask-Script manager that creates a test request context"""
    def create_app(self, **kwargs):
        app = super(ContextfulManager, self).create_app(**kwargs)
        app.test_request_context().__enter__()
        return app
