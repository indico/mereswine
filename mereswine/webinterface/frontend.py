import itertools

from collections import Counter
from flask import Blueprint, current_app, render_template, jsonify, g, request, session, url_for

from ..core import db, multipass
from ..menu import menu, breadcrumb, make_breadcrumb
from ..models import Instance
from ..utils import aggregate_values, aggregate_chart
from .. import crawler


bp = Blueprint('frontend', __name__)


def get_all_server_fields(server_list):
    extra_fields = set()
    for server in server_list:
        extra_fields.update(get_server_fields(server) or {})
    return sorted(extra_fields)


def get_server_fields(server):
    extra_fields = set()
    fields_settings = current_app.config['CRAWLED_FIELDS_SETTINGS']
    if server.crawled_data:
        data = {k: v for k, v in server.crawled_data.items() if fields_settings.get(k, object()) is not None}
        extra_fields.update(data or {})
    return sorted(extra_fields)


@bp.before_request
def login_required():
    whitelist = current_app.config['USER_WHITELIST']
    if 'user' not in session or session['user'] not in whitelist.get(session.get('provider'), set()):
        next_url = request.full_path.rstrip('?')
        return multipass.logout(url_for('auth.login', next=next_url), clear_session=True)


@bp.route('/logout')
def logout():
    return multipass.logout(url_for('auth.index'), clear_session=True)


@bp.route('/servers')
@menu('server_list')
@breadcrumb('Servers', '.server_list')
def server_list():
    g.breadcrumbs.append(make_breadcrumb('Server list'))
    server_list = Instance.query.all()
    active_instances = sum(1 for server in server_list if server.enabled)
    wvars = {
        'server_list': server_list,
        'extra_fields': get_all_server_fields(server_list),
        'active_instances': active_instances
    }
    return render_template('server_list.html', **wvars)


@bp.route('/servers/<id>', methods=('DELETE',))
def remove_server(id):
    instance = Instance.query.filter_by(id=id).first()
    db.session.delete(instance)
    db.session.commit()
    return jsonify()


@bp.route('/servers/<id>', methods=('POST',))
def update_server(id):
    instance = Instance.query.filter_by(id=id).first()
    crawl = request.form.get('crawl', False)
    if crawl:
        crawler.crawl_instance(instance)
    else:
        instance.url = request.form['url'].rstrip('/')
        instance.contact = request.form['contact']
        instance.email = request.form['email']
        instance.organization = request.form['organization']
        instance.enabled = request.form['enabled'] == 'true'
        db.session.commit()
    return jsonify()


@bp.route('/servers/<id>')
@breadcrumb('Servers', '.server_list')
def get_server(id):
    instance = Instance.query.filter_by(id=id).first()
    title = crawler.trim_url(instance.url)
    g.breadcrumbs.append(make_breadcrumb(title))
    wvars = {
        'server': instance,
        'fields': get_server_fields(instance),
        'title': title
    }
    return render_template('manage_server.html', **wvars)


@bp.route('/servers', methods=('POST',))
def crawl_all():
    crawler.crawl_all()
    return jsonify()


@bp.route('/statistics')
@menu('statistics')
@breadcrumb('Statistics', '.statistics')
def statistics():
    server_list = Instance.query.all()
    extra_fields = get_all_server_fields(server_list)
    extended_instances = []
    country_names = []
    country_codes = []
    markers = []
    id_mapping = {}
    dates = []
    i = 0

    for server in server_list:
        dates.append(server.registration_date.date())
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

    count = 0
    registration_counts = []
    for date, items in itertools.groupby(sorted(dates)):
        count += sum(1 for _ in items)
        registration_counts.append((date.strftime('%Y-%m-%d'), count))

    wvars = {
        'country_names': Counter(country_names),
        'country_codes': Counter(country_codes),
        'markers': markers,
        'id_mapping': id_mapping,
        'additional_charts': additional_charts,
        'registration_counts': registration_counts
    }
    return render_template('statistics.html', **wvars)
