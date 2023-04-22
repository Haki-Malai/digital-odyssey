from flask import g, current_app, redirect, request
from flask_login import current_user, login_required
from apifairy import response

from app import db
from app.user import bp
from app.models import Product
from app.api.schemas import CartSchema

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
def add_wishlist(product_id: int) -> str:
    """Add a product to the current user's wishlist.
    :param product_id: the product id
    """
    if Product.query.get(product_id) is not  None:
        current_user.wishlist.add_product(product_id)
        db.session.commit()

    return redirect(request.referrer)


@bp.route('/cart')
@login_required
@response(cart_schema)
def cart() -> dict:
    """Get the current user's cart.
    """
    return current_user.cart


@bp.route('/cart/<int:product_id>/<int:quantity>')
@login_required
def add_cart(product_id: int, quantity:int) -> object:
    """Add or update quantity of product in cart.
    :param product_id: the product id
    :param quantity: the quantity to add
    """
    if Product.query.get(product_id) is not  None:
        current_user.cart.add_product(product_id, quantity)
        db.session.commit()

    return redirect(request.referrer)


@bp.route('/checkout')
@login_required
def checkout() -> dict:
    """Checkout the current user's cart.
    """
    return current_user.cart.products
