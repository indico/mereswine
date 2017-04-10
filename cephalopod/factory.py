from celery import Celery
from flask import Flask, current_app, flash, session, url_for
from flask_multipass import Multipass

from .core import assets, db, babel
from .assets import version_url, versioned_static_file
from .menu import setup_breadcrumbs
from .utils import pretty_name, aggregate
from .webinterface import bp as webinterface_bp
from .api import bp as api_bp
# noinspection PyUnresolvedReferences
from . import models  # registers db models

multipass = Multipass()


def make_app():
    """Returns a :class:`CustomFlask` application instance that is properly configured."""
    app = Flask('cephalopod')
    app.config.from_pyfile('settings.cfg.example')  # In case a custom option is missing in settings.cfg
    app.config.from_pyfile('settings.cfg')
    assets.init_app(app)
    db.init_app(app)
    babel.init_app(app)
    register_core_funcs(app)
    register_blueprints(app)
    multipass.init_app(app)
    return app


def register_core_funcs(app):
    """Registers core functionality on the app that does not fit into Blueprints."""
    # versioned assets
    app.add_url_rule('/static_v/<version>/<path:filename>', view_func=versioned_static_file)
    app.add_template_filter(version_url)
    # breadcrumb nav
    app.before_request(setup_breadcrumbs)
    # template filters
    app.add_template_filter(pretty_name)
    app.add_template_filter(aggregate)


def register_blueprints(app):
    """Registers our blueprints."""
    app.register_blueprint(webinterface_bp)
    app.register_blueprint(api_bp, url_prefix='/api')


def make_celery(app=None):
    if app is None:
        app = make_app()
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


@multipass.identity_handler
def identity_handler(identity_info):
    """Implements the Flask-Multipass identity handler"""
    email = identity_info.data['email']
    if email in current_app.config['USER_WHITELIST']:
        session['user_email'] = email
        session['username'] = identity_info.data['username']
        flash('You were successfully logged in', 'success')
    else:
        multipass.logout(url_for('.login'), clear_session=True)
        flash('You are not allowed to log in', 'error')
