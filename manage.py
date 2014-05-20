from flask import current_app
from flask.ext.script import Manager, prompt_bool

from tracker import models, crawler
from tracker.core import db, ContextfulManager
from tracker.factory import make_app


manager = ContextfulManager(make_app)
db_manager = Manager(help='Manage database')
manager.add_command('db', db_manager)


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
def create_user(username, password, email):
    user = models.User(username, password, email)
    db.session.add(user)
    db.session.commit()


@manager.shell
def shell_context():
    ctx = {'db': db}
    ctx.update((x, getattr(models, x)) for x in dir(models) if x[0].isupper())
    return ctx


if __name__ == '__main__':
    manager.run()
