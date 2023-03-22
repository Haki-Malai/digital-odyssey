from flask import jsonify
from flask_login import current_user, login_required

from app import db
from app.api import bp
from app.models import Product


@bp.route('/cart', methods=['GET'])
@login_required
def cart():
    return current_user.cart.cart_products


@bp.route('/cart/<int:product_id>/<int:quantity>', methods=['GET'])
@login_required
def cart_quantity(product_id, quantity):
    # Update the quantity in the database
    product = Product.query.get(product_id)
    current_user.cart.update_quantity(product, quantity)
    db.session.commit()
    return jsonify({
        'product_quantity': quantity,
        'total_price': current_user.cart.total_price,
        'product_total_price': current_user.cart.cart_product_total_price(product),
        'product_total_sale_price': current_user.cart.cart_product_total_sale_price(product),
    })