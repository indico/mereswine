from flask import render_template, g

from ..menu import menu, breadcrumb, make_breadcrumb
from . import bp


@bp.route('/')
@menu('index')
@breadcrumb('Home', '.index')
def index():
    g.breadcrumbs.append(make_breadcrumb('Lorem Ipsum'))
    g.breadcrumbs.append(make_breadcrumb('Dynamic Breadcrumb'))
    return render_template('index.html')
