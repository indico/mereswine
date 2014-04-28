from flask.ext.assets import Environment
from flask.ext.script import Manager
from flask.ext.sqlalchemy import SQLAlchemy


# Flask extensions
assets = Environment()
db = SQLAlchemy()


class ContextfulManager(Manager):
    """Flask-Script manager that creates a test request context"""
    def create_app(self, **kwargs):
        app = super(ContextfulManager, self).create_app(**kwargs)
        app.test_request_context().__enter__()
        return app
