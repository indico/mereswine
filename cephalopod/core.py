from flask.ext.assets import Environment
from flask.ext.babel import Babel
from flask.ext.sqlalchemy import SQLAlchemy
from flask_multipass import Multipass


# Flask extensions
assets = Environment()
db = SQLAlchemy()
babel = Babel()
multipass = Multipass()
