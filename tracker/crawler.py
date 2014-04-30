import json
import requests
from datetime import datetime

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
    inferred_data = crawl_statistics(instance)
    inferred_data.update(crawl_system_info(instance))
    instance.crawled_data = json.dumps(inferred_data)
    instance.crawl_date = datetime.utcnow()
    db.session.commit()


def crawl_all():
    instances = Instance.query.filter_by(enabled=True).all()
    for instance in instances:
        crawl_instance(instance)
