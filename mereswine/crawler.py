import logging
from datetime import datetime

import requests
from flask import current_app

from .core import db
from .models import Instance


def trim_url(url):
    short_url = url
    try:
        short_url = short_url[short_url.index('//')+2:]
    except ValueError:
        pass
    try:
        short_url = short_url[:short_url.index(':')]
    except ValueError:
        pass
    try:
        short_url = short_url[short_url.index('www.')+4:]
    except ValueError:
        pass
    return short_url


def crawl(instance):
    crawling_endpoints = current_app.config['CRAWLING_ENDPOINTS']
    base_url = instance.url
    crawled_data = {}
    for endpoint in crawling_endpoints:
        try:
            endpoint_url = endpoint['url']
        except KeyError:
            continue
        url = '{0}{1}'.format(base_url, endpoint_url)
        headers = endpoint.get('headers', None)
        r = requests.get(url, headers=headers, verify=not current_app.config['DEBUG'])
        crawled_data.update(r.json())
    instance.crawled_data = crawled_data
    instance.crawl_date = datetime.utcnow()
    db.session.commit()


def geolocate(instance):
    url = 'http://freegeoip.net/json/{0}'.format(trim_url(instance.url))
    r = requests.get(url)
    geolocation = r.json()
    instance.geolocation = geolocation
    db.session.commit()


def crawl_instance(instance):
    if not isinstance(instance, Instance):
        instance = Instance.query.filter_by(uuid=instance).one()

    try:
        crawl(instance)
    except Exception:
        logging.exception("cannot crawl instance {0}".format(instance.uuid))
    else:
        logging.info("successfully crawled instance {0}".format(instance.uuid))

    try:
        geolocate(instance)
    except Exception:
        logging.exception("cannot geolocate instance {0}".format(instance.uuid))
    else:
        logging.info("successfully geolocated instance {0}".format(instance.uuid))


def crawl_all():
    instances = Instance.query.filter_by(enabled=True).all()
    for instance in instances:
        crawl_instance(instance)
