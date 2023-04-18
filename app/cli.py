import click
from flask import Blueprint

bp = Blueprint('cli', __name__, cli_group=None)


@bp.cli.command('fake')
def fake() -> None:
    """Generate fake data.
    """
    from app.fake import create_users, create_categories, create_subcategories, \
        create_brands, create_products, create_fake_banners, create_fake_admin

    click.echo('Creating default admin...')
    create_fake_admin()

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

    click.echo('Creating banners...')
    create_fake_banners()

    click.echo('Done.')
