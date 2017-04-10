import sys

from flask import current_app
from flask.ext.script import Manager, Server, prompt_bool

from . import models, crawler
from .core import db, ContextfulManager
from .factory import make_app
from .tasks import celery


manager = ContextfulManager(make_app)
db_manager = Manager(help='Manage database')
manager.add_command('db', db_manager)
app = manager.app()
if app.config.get('SSL_CERT') and app.config.get('SSL_KEY'):
    manager.add_command('runserver',
                        Server(ssl_context=(app.config.get('SSL_CERT'), app.config.get('SSL_KEY'))))


@db_manager.command
def drop():
    """Drops all database tables"""
    if prompt_bool('Are you sure you want to lose all your data?'):
        db.drop_all()


@db_manager.command
def create():
    """Creates database tables"""
    with current_app.test_request_context():
        db.create_all()


@db_manager.command
def recreate():
    """Recreates database tables (same as issuing 'drop' and then 'create')"""
    drop()
    create()


@manager.command
def crawl(uuid=None):
    if uuid is not None:
        crawler.crawl_instance(uuid)
    else:
        crawler.crawl_all()


@manager.command
def runworker(concurrency='4'):
    """Runs the celery worker"""
    args = sys.argv[:1]
    args += ('-c', concurrency)
    args += ('-B',)
    celery.worker_main(args)


@manager.shell
def shell_context():
    ctx = {'db': db}
    ctx.update((x, getattr(models, x)) for x in dir(models) if x[0].isupper())
    return ctx


def main():
    manager.run()
