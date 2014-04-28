import json
import requests
from datetime import datetime

from ..core import db
from ..models import Instance


def crawl_instance(instance):
    if not isinstance(instance, Instance):
        instance = Instance.query.filter_by(uuid=instance).one()
    url = '{0}/category/0/statistics'.format(instance.url)
    headers = {'Accept': 'application/json'}
    r = requests.get(url, headers=headers)
    statistics = r.json()
    instance.crawled_data = json.dumps(statistics)
    instance.crawl_date = datetime.utcnow()
    db.session.commit()


def crawl_all():
    instances = Instance.query.filter_by(enabled=True).all()
    for instance in instances:
        crawl_instance(instance)
