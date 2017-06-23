from flask import Blueprint, render_template

from ..menu import menu, breadcrumb
from ..core import multipass


bp = Blueprint('auth', __name__)


@bp.route('/')
@menu('index')
@breadcrumb('Home', '.index')
def index():
    return render_template('index.html')


@bp.route('/login/', methods=('GET', 'POST'))
@bp.route('/login/<provider>', methods=('GET', 'POST'))
def login(provider=None):
    return multipass.process_login(provider)
