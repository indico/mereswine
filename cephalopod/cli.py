import click

from celery.bin.celery import CeleryCommand, command_classes
from flask.cli import FlaskGroup

from . import crawler
from .factory import make_app
from .core import db


def shell_ctx():
    from . import models
    ctx = {'db': db}
    ctx.update((x, getattr(models, x)) for x in dir(models) if x[0].isupper())
    return ctx


def register_shell_ctx(app):
    app.shell_context_processor(shell_ctx)


@click.group(cls=FlaskGroup, create_app=make_app)
def cli():
    """
    This script lets you control various aspects of Cephalopod from the
    command line.
    """


@cli.group(name='db')
def db_cli():
    """DB management commands"""
    pass


@db_cli.command()
def drop():
    """Drop all database tables"""
    if click.confirm('Are you sure you want to lose all your data?'):
        db.drop_all()


@db_cli.command()
def create():
    """Create database tables"""
    db.create_all()


@db_cli.command()
def recreate():
    """Recreate database tables (same as issuing 'drop' and then 'create')"""
    if click.confirm('Are you sure you want to lose all your data?'):
        db.drop_all()
        db.create_all()


@cli.command()
@click.option('--uuid', help="UUID of server to crawl")
def crawl(uuid):
    """Crawl all instances, or a given UUID if passed"""
    if uuid is not None:
        crawler.crawl_instance(uuid)
    else:
        crawler.crawl_all()


@cli.command(context_settings={'ignore_unknown_options': True, 'allow_extra_args': True}, add_help_option=False)
@click.pass_context
def celery(ctx):
    """Manage the Celery task daemon."""
    from .tasks import celery
    # remove the celery shell command
    next(funcs for group, funcs, _ in command_classes if group == 'Main').remove('shell')
    del CeleryCommand.commands['shell']
    CeleryCommand(celery).execute_from_commandline(['flask celery'] + ctx.args)
