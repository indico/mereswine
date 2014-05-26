import logging
from datetime import datetime

import requests

from .core import db
from .models import Instance


def trim_url(url):
    short_url = url[url.index('//')+2:]
    try:
        short_url = short_url[:short_url.index(':')]
    except ValueError:
        pass
    try:
        short_url = short_url[short_url.index('www.')+4:]
    except ValueError:
        pass
    return short_url


def crawl_statistics(instance):
    url = '{0}/category/0/statistics'.format(instance.url)
    headers = {'Accept': 'application/json'}
    r = requests.get(url, headers=headers)
    return r.json()


def crawl_system_info(instance):
    url = '{0}/system-info'.format(instance.url)
    r = requests.get(url)
    return r.json()


def crawl_data(instance):
    crawled_data = crawl_statistics(instance)
    crawled_data.update(crawl_system_info(instance))
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
        crawl_data(instance)
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
