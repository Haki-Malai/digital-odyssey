from flask import g, current_app, flash, redirect, url_for
from flask_login import current_user, login_required
from apifairy import response

from app import db
from app.user import bp
from app.models import Product
from app.api.schemas import CartSchema, EmptySchema

cart_schema = CartSchema()


@bp.before_app_request
def before_request() -> None:
    """Set search form to the global config.
    """
    g.config = current_app.config


@bp.route('/user')
@login_required
def user() -> str:
    """Get the current user.
    """
    return current_user.username


@bp.route('/wishlist')
@login_required
def wishlist() -> dict:
    """Get the current user's wishlist.
    """
    return current_user.wishlist.products


@bp.route('/wishlist/<int:product_id>')
@login_required
def wishlist_product(product_id: int) -> dict:
    """Add a product to the current user's wishlist.
    :param product_id: the product id
    """
    product = Product.query.get(product_id)
    current_user.wishlist.add(product)
    db.session.commit()
    return current_user.wishlist.products


@bp.route('/cart')
@login_required
@response(cart_schema)
def cart() -> dict:
    """Get the current user's cart.
    """
    return current_user.cart


@bp.route('/cart/<int:product_id>/<int:quantity>')
@login_required
@response(EmptySchema, 200)
def cart_quantity(product_id: int, quantity:int) -> object:
    """Add or update quantity of product in cart.
    :param product_id: the product id
    :param quantity: the quantity to add
    """
    if current_user.add_to_cart(product_id, quantity):
        return {}

    flash(400, 'There was an error adding the product to the cart')
    return redirect(url_for('main.index'))


@bp.route('/checkout')
@login_required
def checkout() -> dict:
    """Checkout the current user's cart.
    """
    return current_user.cart.products
