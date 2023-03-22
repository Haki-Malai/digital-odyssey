from flask import current_app, render_template, request, g, jsonify
from flask_login import current_user, login_required
from app import db
from app.main import bp
from app.main.forms import SearchForm
from app.models import User, Category, Subcategory, Product


@bp.before_app_request
def before_request():
    g.search_form = SearchForm()


@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html',
                           config=current_app.config,
                           categories=Category.query.all(),
                           current_user=current_user)


@bp.route('/user', methods=['GET'])
@login_required
def user():
    return current_user.username


@bp.route('/wishlist', methods=['GET'])
@login_required
def wishlist():
    return current_user.wishlist.products


@bp.route('/checkout', methods=['GET'])
@login_required
def checkout():
    return current_user.cart.products


@bp.route('/products', methods=['GET'])
def products():
    return Product.query.first().name


@bp.route('/product/<int:product_id>', methods=['GET'])
def product(product_id):
    return Product.query.get(product_id).name


@bp.route('/category/<int:category_id>', methods=['GET'])
def category(category_id):
    return Category.query.get(category_id).name


@bp.route('/subcategory/<int:subcategory_id>', methods=['GET'])
def subcategory(subcategory_id):
    return Subcategory.query.get(subcategory_id).name


@bp.route('/search')
def search():
    page = request.args.get('page', 1, type=int)
    products, total = Product.search(g.search_form.q.data, page,
                               current_app.config['ITEMS_PER_PAGE'])
    return jsonify({ products })