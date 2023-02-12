from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, UserMixin, AnonymousUserMixin
from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    role = db.Column(db.String(64), default='user')
    password_hash = db.Column(db.String(128))

    cart = db.relationship('Cart', back_populates='user', uselist=False)
    wishlist = db.relationship('Wishlist', back_populates='user', uselist=False)

    def __repr__(self) -> str:
        return '<User %r>' % self.username

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Currently only 2 roles: admin and user so this is fine
    def has_permission(self, permission):
        return self.role == permission
    
    # Cart methods
    def add_to_cart(self, product, quantity):
        if not self.cart:
            self.cart = Cart(user=self)
        self.cart.add_product(product, quantity)

    def remove_from_cart(self, product):
        if self.cart:
            self.cart.remove_product(product)

    def empty_cart(self):
        if self.cart:
            self.cart.empty_cart()
    
    # Wishlist methods
    def add_to_wishlist(self, product):
        if not self.wishlist:
            self.wishlist = Wishlist(user=self)
        self.wishlist.add_product(product)

    def remove_from_wishlist(self, product):
        if product in self.wishlist:
            self.wishlist.remove(product)


class AnonymousUser(AnonymousUserMixin):
    def has_permission(self, permission):
        return False
    
    def is_administrator(self):
        return False

login.anonymous_user = AnonymousUser


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(64), unique=True, index=True)

    subcategories = db.relationship('Subcategory', back_populates='category')
    products = db.relationship('Product', back_populates='category')

    def __repr__(self):
        return '<Category %r>' % self.name


class Subcategory(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(124), index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    category = db.relationship('Category', back_populates='subcategories')
    products = db.relationship('Product', back_populates='subcategory')

    def __repr__(self):
        return '<Subcategory %r>' % self.name


class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)

    products = db.relationship('Product', back_populates='brand')
        
    def __repr__(self):
        return '<Brand %r>' % self.name


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategory.id'), nullable=False)

    category = db.relationship('Category', back_populates='products')
    subcategory = db.relationship('Subcategory', back_populates='products')
    brand = db.relationship('Brand', back_populates='products')
    variations = db.relationship('Variation', back_populates='product')
        
    def __repr__(self):
        return '<Product %r>' % self.name

    def create_variation(self, name):
        variation = Variation(name=name, product_id=self.id)
        db.session.add(variation)
        return variation


class Variation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    values = db.relationship('VariationValue', back_populates='variation')
    product = db.relationship('Product', back_populates='variations')

    def __repr__(self):
        return '<Variation %r>' % self.name

    def create_value(self, name):
        variant_value = VariationValue(name=name, variation_id=self.id, product_id=self.product_id)
        db.session.add(variant_value)


class VariationValue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    variation_id = db.Column(db.Integer, db.ForeignKey('variation.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    variation = db.relationship('Variation', back_populates='values')

    def __repr__(self):
        return '<VariationValue %r>' % self.name


class WishlistProduct(db.Model):
    wishlist_id = db.Column(db.Integer, db.ForeignKey('wishlist.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)

    product = db.relationship('Product', lazy='joined')
    wishlist = db.relationship('Wishlist', back_populates='products')


class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship('User', back_populates='wishlist')
    products = db.relationship('WishlistProduct', back_populates='wishlist')

    def __repr__(self):
        return '<Wishlist %r>' % self.user.username
    
    def add_product(self, product):
        cp = WishlistProduct(wishlist=self, product=product)
        db.session.add(cp)


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship('User', back_populates='cart')
    products = db.relationship('CartProduct', back_populates='cart')

    def __repr__(self):
        return '<Cart %r>' % self.user.username

    @property
    def total_price(self):
        return sum(cp.total_price for cp in self.products)

    def add_product(self, product, quantity=1, variation_value_id=None):
        # Need to add self to session first
        db.session.add(self)
        for cp in self.products:
            if cp.product == product:
                cp.quantity += quantity
                cp.total_price += (quantity * product.price)
                return
        if not variation_value_id: variation_value_id = product.variations[0].values[0].id
        cp = CartProduct(cart=self, product=product, quantity=quantity, \
            total_price=(quantity * product.price), variation_value_id=variation_value_id)
        db.session.add(cp)

    def empty_cart(self):
        self.products = []
        

class CartProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, nullable=False, default=0)
    total_price = db.Column(db.Float, nullable=False, default=0.0)
    variation_value_id = db.Column(db.Integer, db.ForeignKey('variation_value.id'))

    cart = db.relationship('Cart', back_populates='products')
    product = db.relationship('Product', lazy='joined')
    variation_value = db.relationship('VariationValue', lazy='joined')