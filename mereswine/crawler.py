import logging
from datetime import datetime
from urllib.parse import urlparse

import requests
import socket
from flask import current_app

from .core import db
from .models import Instance


GEOLOCATION_URL = 'https://api.ipgeolocation.io/ipgeo'


def crawl(instance):
    crawling_endpoints = current_app.config['CRAWLING_ENDPOINTS']
    base_url = instance.url
    crawled_data = {}
    for endpoint in crawling_endpoints:
        try:
            endpoint_url = endpoint['url']
            logging.debug("Crawling endpoint '%s'", endpoint_url)
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
    api_key = current_app.config['IP_GEOLOCATION_API_KEY']

    if not api_key:
        logging.warn('Geolocation API key not set. Geolocation is off.')
        return

    url = urlparse(instance.url).hostname

    try:
        ip_address = socket.gethostbyname(url)
    except socket.gaierror:
        logging.warn("Geolocation: couldn't resolve %s", url)
        return

    r = requests.get(GEOLOCATION_URL, params={
        'ip': ip_address,
        'apiKey': api_key
    })
    geolocation = r.json()

    if 'message' in geolocation:
        # The API returned an error
        logging.error('Geolocation failed for %s: %s', url, geolocation['message'])
        return

    instance.geolocation = geolocation
    db.session.commit()


def crawl_instance(instance):
    if not isinstance(instance, Instance):
        instance = Instance.query.filter_by(uuid=instance).one()

    logging.info("Crawling %s [%s]", instance.url, instance.uuid)

    try:
        crawl(instance)

        try:
            geolocate(instance)
        except Exception:
            logging.error("Cannot geolocate instance %s", instance.uuid)
        else:
            logging.info("successfully geolocated instance %s", instance.uuid)
    except requests.ConnectionError:
        logging.error('Cannot crawl instance %s: Connection error', instance.uuid)
    except Exception:
        logging.exception("Cannot crawl instance %s", instance.uuid)
    else:
        logging.info("Successfully crawled instance %s", instance.uuid)



def crawl_all():
    instances = Instance.query.filter_by(enabled=True).all()
    for instance in instances:
        crawl_instance(instance)
