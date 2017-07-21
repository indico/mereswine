import csscompressor
from flask_assets import Environment
from flask_babel import Babel
from flask_mail import Mail
from flask_multipass import Multipass
from flask_sqlalchemy import SQLAlchemy
from webassets.filter import register_filter, Filter


# Flask extensions
assets = Environment()
db = SQLAlchemy()
babel = Babel()
multipass = Multipass()
mail = Mail()


@register_filter
class CSSCompressor(Filter):
    name = 'csscompressor'

    def output(self, _in, out, **kw):
        out.write(csscompressor.compress(_in.read(), max_linelen=500))
