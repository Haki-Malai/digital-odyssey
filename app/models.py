from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, UserMixin, AnonymousUserMixin
from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    role = db.Column(db.String(64), default='user')
    password_hash = db.Column(db.String(128))

    cart = db.relationship('Cart', back_populates='user', uselist=False)

    def __repr__(self) -> str:
        return '<User %r>' % self.username

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    def password(self, password):
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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)

    subcategories = db.relationship('Subcategory', back_populates='category')
    products = db.relationship('Product', back_populates='category')

    def __repr__(self):
        return '<Category %r>' % self.name

    def __init__(self, **kwargs):
        super(Category, self).__init__(**kwargs)


class Subcategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(124), index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    category = db.relationship('Category', back_populates='subcategories')
    products = db.relationship('Product', back_populates='subcategory')

    def __repr__(self):
        return '<Subcategory %r>' % self.name

    def __init__(self, **kwargs):
        super(Subcategory, self).__init__(**kwargs)


class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    products = db.relationship('Product', back_populates='brand')
        
    def __repr__(self):
        return '<Brand %r>' % self.name

    def __init__(self, **kwargs):
        super(Brand, self).__init__(**kwargs)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategory.id'), nullable=False)

    category = db.relationship('Category', back_populates='products')
    subcategory = db.relationship('Subcategory', back_populates='products')
    brand = db.relationship('Brand', back_populates='products')
        
    def __repr__(self):
        return '<Product %r>' % self.name

    def __init__(self, **kwargs):
        super(Product, self).__init__(**kwargs)


cart_products = db.Table('cart_products', db.Model.metadata,
    db.Column('cart_id', db.Integer, db.ForeignKey('cart.id')),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'))
)


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship('User', back_populates='cart')
    cart_products = db.relationship('CartProduct', back_populates='cart')

    @property
    def products(self):
        return [cp.product for cp in self.cart_products]

    @property
    def total_price(self):
        return sum(cp.total_price for cp in self.cart_products)

    def add_product(self, product, quantity=1):
        for cp in self.cart_products:
            if cp.product == product:
                cp.quantity += quantity
                cp.total_price += (quantity * product.price)
                return
        cp = CartProduct(cart=self, product=product, quantity=quantity, total_price=(quantity * product.price))
        db.session.add(cp)
        

class CartProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, nullable=False, default=0)
    total_price = db.Column(db.Float, nullable=False, default=0.0)

    cart = db.relationship('Cart', back_populates='cart_products')
    product = db.relationship('Product', lazy='joined')