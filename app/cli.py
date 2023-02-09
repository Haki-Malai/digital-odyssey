import click
from flask import Blueprint

bp = Blueprint('cli', __name__)


@bp.cli.command('fake')
def fake():
    from app.fake import create_users, create_categories, create_subcategories, \
        create_brands, create_products

    click.echo('Creating users...')
    create_users()

    click.echo('Creating categories...')
    create_categories()

    click.echo('Creating subcategories...')
    create_subcategories()

    click.echo('Creating brands...')
    create_brands()

    click.echo('Creating products...')
    create_products()

    click.echo('Done.')
    