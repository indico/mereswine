from celery import Celery
from flask import Flask, current_app, flash, session, url_for
from werkzeug.contrib.fixers import ProxyFix

from .core import assets, db, babel, multipass
from .assets import version_url, versioned_static_file
from .menu import setup_breadcrumbs
from .utils import pretty_name, aggregate
from webinterface.frontend import bp as frontend_bp
from webinterface.auth import bp as auth_bp
from .api import bp as api_bp
# noinspection PyUnresolvedReferences
from . import models  # registers db models


def make_app():
    """Returns a :class:`CustomFlask` application instance that is properly configured."""
    app = Flask('cephalopod')
    app.config.from_pyfile('settings.cfg.example', silent=True)  # In case a custom option is missing in settings.cfg
    app.config.from_pyfile('settings.cfg')
    assets.init_app(app)
    db.init_app(app)
    babel.init_app(app)
    register_core_funcs(app)
    register_blueprints(app)
    multipass.init_app(app)
    if app.config['USE_PROXY']:
        app.wsgi_app = ProxyFix(app.wsgi_app)
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
    app.register_blueprint(frontend_bp)
    app.register_blueprint(auth_bp)
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
    identifier = identity_info.identifier
    provider = identity_info.provider.name
    whitelist = current_app.config['USER_WHITELIST']
    if provider in whitelist and identifier in whitelist.get(provider, set()):
        session['user'] = identifier
        session['provider'] = provider
        flash('You were successfully logged in', 'success')
    else:
        session.clear()
        flash('You are not allowed to log in', 'error')
        return multipass.logout(url_for('.login'))
