from flask import current_app, render_template, request, g, redirect, url_for
from flask_login import current_user

from app.main import bp
from app.main.forms import SearchForm
from app.models import Category, Subcategory, Product, Banner


@bp.before_app_request
def before_request() -> None:
    """Set search form to the global config.
    """
    g.search_form = SearchForm()
    g.config = current_app.config


@bp.route('/')
def index() -> str:
    """Get the index page.
    """
    return render_template('index.html',
                           categories=Category.query.all(),
                           products=Product.query.all(),
                           banners=Banner.query,
                           current_user=current_user)


@bp.route('/products')
def products() -> str:
    """Get all products.
    """
    return Product.query.first().name


@bp.route('/product/<int:product_id>')
def product(product_id:int) -> str:
    """Get a product.
    :param product_id: The product id.
    """
    return Product.query.get(product_id).name


@bp.route('/product/search')
def product_search() -> str:
    """Search for a product.
    """
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))

    page = request.args.get('page', 1, type=int)
    products, total = Product.search(g.search_form.q.data, page,
                                     current_app.config['ITEMS_PER_PAGE'])

    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['ITEMS_PER_PAGE'] else None

    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None

    return render_template('search.html',
                           categories=Category.query.all(),
                           products=products,
                           next_url=next_url,
                           prev_url=prev_url)


@bp.route('/category/<int:category_id>')
def category(category_id: int) -> str:
    """Get a category.
    :param category_id: The category id.
    """
    return Category.query.get(category_id).name


@bp.route('/subcategory/<int:subcategory_id>')
def subcategory(subcategory_id: int) -> str:
    """Get a subcategory.
    :param subcategory_id: The subcategory id.
    """
    return Subcategory.query.get(subcategory_id).name
