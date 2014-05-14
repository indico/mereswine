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
    server_list = Instance.query.all()
    extra_fields = set()
    for server in server_list:
        extra_fields.update(server.crawled_data or {})
    wvars = {'server_list': server_list,
             'extra_fields': sorted(extra_fields)}
    return render_template('server_list.html', **wvars)


@bp.route('/servers/<id>', methods=('DELETE',))
def remove_server(id):
    instance = Instance.query.filter_by(id=id).first()
    db.session.delete(instance)
    db.session.commit()
    return jsonify()


@bp.route('/servers/<id>', methods=('POST', ))
def update_server(id):
    instance = Instance.query.filter_by(id=id).first()
    crawl = request.form.get('crawl', False)
    if crawl:
        crawler.crawl_instance(instance)
    else:
        instance.uuid = request.form['uuid']
        instance.url = request.form['url'].rstrip('/')
        instance.contact = request.form['contact']
        instance.email = request.form['email']
        instance.organisation = request.form['organisation']
        instance.enabled = True if request.form['enabled'] == 'true' else False
        db.session.commit()
    return jsonify()


@bp.route('/servers/<id>')
@breadcrumb('List of servers', '.server_list')
def get_server(id):
    instance = Instance.query.filter_by(id=id).first()
    title = instance.url[instance.url.index('//')+2:]
    try:
        title = title[:title.index(':')]
    except ValueError:
        pass
    try:
        title = title[title.index('www.')+4:]
    except ValueError:
        pass
    g.breadcrumbs.append(make_breadcrumb(title))
    wvars = {'server': instance,
             'title': title}
    return render_template('manage_server.html', **wvars)


@bp.route('/servers', methods=('POST', ))
def crawl_all():
    crawler.crawl_all()
    return jsonify()


@bp.route('/statistics')
@menu('statistics')
@breadcrumb('Statistics', '.statistics')
def statistics():
    return render_template('statistics.html')
