from flask import Blueprint

from cephalopod.core import multipass

bp = Blueprint('auth', __name__)


@bp.route('/login/', methods=('GET', 'POST'))
@bp.route('/login/<provider>', methods=('GET', 'POST'))
def login(provider=None):
    return multipass.process_login(provider)
