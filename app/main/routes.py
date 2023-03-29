from flask import current_app, render_template, request, g, abort, \
    redirect, url_for
from flask_login import current_user, login_required
from apifairy import response

from app import db
from app.main import bp
from app.main.forms import SearchForm
from app.models import User, Category, Subcategory, Product, Banner
from app.api.schemas import CartSchema, EmptySchema

cart_schema = CartSchema()


@bp.before_app_request
def before_request():
    g.search_form = SearchForm()
    g.config = current_app.config


@bp.route('/')
def index():
    return render_template('index.html',
                           categories=Category.query.all(),
                           products=Product.query.all(),
                           banners=Banner.query,
                           current_user=current_user)


@bp.route('/user')
@login_required
def user():
    return current_user.username


@bp.route('/wishlist')
@login_required
def wishlist():
    return current_user.wishlist.products


@bp.route('/wishlist/<int:product_id>')
@login_required
def wishlist_product(product_id):
    product = Product.query.get(product_id)
    current_user.wishlist.add(product)
    db.session.commit()
    return current_user.wishlist.products


@bp.route('/cart')
@login_required
@response(cart_schema)
def cart():
    return current_user.cart


@bp.route('/cart/<int:product_id>/<int:quantity>')
@login_required
@response(EmptySchema, 200)
def cart_quantity(product_id, quantity=1):
    """Add or update quantity of product in cart.
    """
    if current_user.add_to_cart(product_id, quantity):
        return {}
    abort(400, 'There was an error adding the product to the cart')


@bp.route('/checkout')
@login_required
def checkout():
    return current_user.cart.products


@bp.route('/products')
def products():
    return Product.query.first().name


@bp.route('/product/<int:product_id>')
def product(product_id):
    return Product.query.get(product_id).name


@bp.route('/product/search')
def product_search():
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
def category(category_id):
    return Category.query.get(category_id).name


@bp.route('/subcategory/<int:subcategory_id>')
def subcategory(subcategory_id):
    return Subcategory.query.get(subcategory_id).name