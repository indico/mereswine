from flask import Flask

from .core import assets, db
from .assets import version_url, versioned_static_file
from .menu import setup_breadcrumbs
from .webinterface import bp as webinterface_bp
from .api import bp as api_bp
# noinspection PyUnresolvedReferences
from . import models  # registers db models


def make_app():
    """Returns a :class:`CustomFlask` application instance that is properly configured."""
    app = Flask('tracker')
    app.config.from_pyfile('settings.cfg.example')  # In case a custom option is missing in settings.cfg
    app.config.from_pyfile('settings.cfg')
    assets.init_app(app)
    db.init_app(app)
    register_core_funcs(app)
    register_blueprints(app)
    return app


def register_core_funcs(app):
    """Registers core functionality on the app that does not fit into Blueprints."""
    # versioned assets
    app.add_url_rule('/static_v/<version>/<path:filename>', view_func=versioned_static_file)
    app.add_template_filter(version_url)
    # breadcrumb nav
    app.before_request(setup_breadcrumbs)


def register_blueprints(app):
    """Registers our blueprints."""
    app.register_blueprint(webinterface_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
