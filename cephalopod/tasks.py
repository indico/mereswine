from .factory import make_celery
from . import crawler

celery = make_celery()

crawl_all_task = celery.task(crawler.crawl_all)
