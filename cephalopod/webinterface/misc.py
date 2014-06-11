import bcrypt
from collections import Counter
from flask import render_template, jsonify, g, request, flash, redirect, url_for
from flask.ext.login import login_user, logout_user, login_required

from ..core import db
from ..menu import menu, breadcrumb, make_breadcrumb
from ..models import Instance, User
from ..utils import aggregate_values, aggregate_chart
from .. import crawler
from . import bp


def get_extra_fields(server_list):
    extra_fields = set()
    for server in server_list:
        extra_fields.update(server.crawled_data or {})
    return sorted(extra_fields)


@bp.route('/')
@menu('index')
@breadcrumb('Home', '.index')
def index():
    return render_template('index.html')


@bp.route('/login', methods=('POST',))
def login():
    username = request.form['username']
    password = request.form['password']
    registered_user = User.query.filter_by(username=username).first()
    if registered_user is None or bcrypt.hashpw(password.encode('utf-8'),
                                                registered_user.password.encode('utf-8')) != registered_user.password:
        flash('Invalid username and/or password', 'error')
    else:
        remember = True if 'remember' in request.form else False
        login_user(registered_user, remember=remember)
    return redirect(request.form["next"] or url_for(".index"))


@bp.route('/logout', methods=('POST',))
@login_required
def logout():
    logout_user()
    return redirect(url_for('.index'))


@bp.route('/servers')
@menu('server_list')
@login_required
@breadcrumb('Servers', '.server_list')
def server_list():
    g.breadcrumbs.append(make_breadcrumb('Server list'))
    server_list = Instance.query.all()
    wvars = {
        'server_list': server_list,
        'extra_fields': get_extra_fields(server_list)
    }
    return render_template('server_list.html', **wvars)


@bp.route('/servers/<id>', methods=('DELETE',))
@login_required
def remove_server(id):
    instance = Instance.query.filter_by(id=id).first()
    db.session.delete(instance)
    db.session.commit()
    return jsonify()


@bp.route('/servers/<id>', methods=('POST',))
@login_required
def update_server(id):
    instance = Instance.query.filter_by(id=id).first()
    crawl = request.form.get('crawl', False)
    if crawl:
        crawler.crawl_instance(instance)
    else:
        instance.url = request.form['url'].rstrip('/')
        instance.contact = request.form['contact']
        instance.email = request.form['email']
        instance.organisation = request.form['organisation']
        instance.enabled = request.form['enabled'] == 'true'
        db.session.commit()
    return jsonify()


@bp.route('/servers/<id>')
@login_required
@breadcrumb('Servers', '.server_list')
def get_server(id):
    instance = Instance.query.filter_by(id=id).first()
    title = crawler.trim_url(instance.url)
    g.breadcrumbs.append(make_breadcrumb(title))
    wvars = {
        'server': instance,
        'title': title
    }
    return render_template('manage_server.html', **wvars)


@bp.route('/servers', methods=('POST',))
@login_required
def crawl_all():
    crawler.crawl_all()
    return jsonify()


@bp.route('/statistics')
@menu('statistics')
@login_required
@breadcrumb('Statistics', '.statistics')
def statistics():
    server_list = Instance.query.all()

    extra_fields = get_extra_fields(server_list)
    extended_instances = []
    country_names = []
    country_codes = []
    markers = []
    id_mapping = {}
    i = 0

    for server in server_list:
        if server.geolocation:
            country_names.append(server.geolocation['country_name'])
            country_codes.append(server.geolocation['country_code'])
            markers.append({
                'latLng': [server.geolocation['latitude'], server.geolocation['longitude']],
                'name': crawler.trim_url(server.url)
            })
            id_mapping[i] = server.id
            i += 1
        else:
            country_names.append('Unknown')
        extended_instances.append({
            'instance': server,
            'fields': aggregate_values(server, extra_fields)
        })
    additional_charts = aggregate_chart(extended_instances, extra_fields)

    wvars = {
        'country_names': Counter(country_names),
        'country_codes': Counter(country_codes),
        'markers': markers,
        'id_mapping': id_mapping,
        'additional_charts': additional_charts
    }
    return render_template('statistics.html', **wvars)
