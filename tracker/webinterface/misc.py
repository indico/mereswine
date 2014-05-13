from flask import render_template, jsonify, g, request

from ..core import db
from ..menu import menu, breadcrumb, make_breadcrumb
from ..models import Instance
from .. import crawler
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
             'extra_fields': sorted(extra_fields)}
    return render_template('server_list.html', **wvars)


@bp.route('/servers/<uuid>', methods=('DELETE',))
def remove_server(uuid):
    instance = Instance.query.filter_by(uuid=uuid).first()
    db.session.delete(instance)
    db.session.commit()
    return jsonify()


@bp.route('/servers/<uuid>', methods=('POST', ))
def update_server(uuid):
    instance = Instance.query.filter_by(uuid=uuid).first()
    crawl = request.form.get('crawl', False)
    if crawl:
        crawler.crawl_instance(uuid)
    else:
        instance.uuid = request.form['uuid']
        instance.url = request.form['url'].rstrip('/')
        instance.contact = request.form['contact']
        instance.email = request.form['email']
        instance.organisation = request.form['organisation']
        instance.enabled = bool(request.form['enabled'])
        db.session.commit()
    return jsonify()


@bp.route('/servers/<uuid>')
@breadcrumb('List of servers', '.server_list')
def get_server(uuid):
    g.breadcrumbs.append(make_breadcrumb('Server management'))
    instance = Instance.query.filter_by(uuid=uuid).first()
    wvars = {'server': instance}
    return render_template('manage_server.html', **wvars)


@bp.route('/statistics')
@menu('statistics')
@breadcrumb('Statistics', '.statistics')
def statistics():
    return render_template('statistics.html')
