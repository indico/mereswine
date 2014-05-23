import requests
from datetime import datetime
import logging

from .core import db
from .models import Instance


def crawl_statistics(instance):
    url = '{0}/category/0/statistics'.format(instance.url)
    headers = {'Accept': 'application/json'}
    r = requests.get(url, headers=headers)
    return r.json()


def crawl_system_info(instance):
    url = '{0}/system-info'.format(instance.url)
    r = requests.get(url)
    return r.json()


def crawl_instance(instance):
    if not isinstance(instance, Instance):
        instance = Instance.query.filter_by(uuid=instance).one()
    try:
        crawled_data = crawl_statistics(instance)
        crawled_data.update(crawl_system_info(instance))
        instance.crawled_data = crawled_data
        instance.crawl_date = datetime.utcnow()
        db.session.commit()
    except Exception:
        logging.exception("cannot crawl instance {0}".format(instance.uuid))
    else:
        logging.info("successfully crawled instance {0}".format(instance.uuid))


def crawl_all():
    instances = Instance.query.filter_by(enabled=True).all()
    for instance in instances:
        crawl_instance(instance)
