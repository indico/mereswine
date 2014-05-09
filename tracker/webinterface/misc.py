from flask import render_template, jsonify

from ..core import db
from ..menu import menu, breadcrumb
from ..models import Instance
from . import bp


@bp.route('/')
@menu('index')
@breadcrumb('Home', '.index')
def index():
    return render_template('index.html')


@bp.route('/servers')
@menu('server_list')
@breadcrumb('List of servers', '.server_list')
def server_list():
    server_list = Instance.query.filter_by(enabled=True).all()
    extra_fields = set()
    for server in server_list:
        extra_fields.update(server.crawled_data or {})
    wvars = {'server_list': server_list,
             'extra_fields': sorted(extra_fields),
             'max_columns': len(extra_fields) + 5}
    return render_template('server_list.html', **wvars)


@bp.route('/servers/<uuid>', methods=('DELETE',))
def remove_server(uuid):
    instance = Instance.query.filter_by(uuid=uuid).first()
    db.session.delete(instance)
    db.session.commit()
    return jsonify()


@bp.route('/statistics')
@menu('statistics')
@breadcrumb('Statistics', '.statistics')
def statistics():
    return render_template('statistics.html')
