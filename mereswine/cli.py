import click
from celery.bin.celery import CeleryCommand, command_classes
from flask.cli import FlaskGroup


# XXX: Do not import any mereswine modules here!
# If any import from this module triggers an exception the dev server
# will die while an exception only happening during app creation will
# be handled gracefully.


def _create_app(info):
    from .factory import make_app
    return make_app()


def shell_ctx():
    from .core import db
    ctx = {'db': db}
    ctx.update((name, cls) for name, cls in db.Model._decl_class_registry.items() if hasattr(cls, '__table__'))
    return ctx


def register_shell_ctx(app):
    app.shell_context_processor(shell_ctx)


@click.group(cls=FlaskGroup, create_app=_create_app)
def cli():
    """
    This script lets you control various aspects of Mereswine from the
    command line.
    """


@cli.group(name='db')
def db_cli():
    """DB management commands"""
    pass


@db_cli.command()
def drop():
    """Drop all database tables"""
    from .core import db
    if click.confirm('Are you sure you want to lose all your data?'):
        db.drop_all()


@db_cli.command()
def create():
    """Create database tables"""
    from .core import db
    db.create_all()


@db_cli.command()
def recreate():
    """Recreate database tables (same as issuing 'drop' and then 'create')"""
    from .core import db
    if click.confirm('Are you sure you want to lose all your data?'):
        db.drop_all()
        db.create_all()


@cli.command()
@click.option('--uuid', help="UUID of server to crawl")
def crawl(uuid):
    """Crawl all instances, or a given UUID if passed"""
    from .crawler import crawl_instance, crawl_all
    if uuid is not None:
        crawl_instance(uuid)
    else:
        crawl_all()


@cli.command(context_settings={'ignore_unknown_options': True, 'allow_extra_args': True}, add_help_option=False)
@click.pass_context
def celery(ctx):
    """Manage the Celery task daemon."""
    from .tasks import celery
    # remove the celery shell command
    next(funcs for group, funcs, _ in command_classes if group == 'Main').remove('shell')
    del CeleryCommand.commands['shell']
    CeleryCommand(celery).execute_from_commandline(['mereswine celery'] + ctx.args)
