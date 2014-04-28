from flask import Blueprint

bp = Blueprint('webinterface', __name__)

from . import misc
