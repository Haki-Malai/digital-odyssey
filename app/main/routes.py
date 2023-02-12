from flask import current_app, render_template
from flask_login import current_user
from app.main import bp
from app.models import User, Category, Subcategory, Product


@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html',
                           config=current_app.config,
                           categories=Category.query.all(),
                           current_user=current_user)

                           
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