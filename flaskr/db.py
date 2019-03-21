import os

import click
from flask import g
from flask.cli import with_appcontext
from peewee import PostgresqlDatabase

database = PostgresqlDatabase(
            os.environ['POSTGRES_DB'],
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
            host=os.environ['POSTGRES_HOST'],
            port=os.environ['POSTGRES_PORT']
        )


def get_db():
    if 'db' not in g:
        g.db = database
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()
    from flaskr.models import User, Post, AuthToken
    db.create_tables([User, Post, AuthToken])


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)