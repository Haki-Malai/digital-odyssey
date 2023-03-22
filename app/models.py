from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, UserMixin, AnonymousUserMixin
from app import db, login
from app.search import add_to_index, remove_from_index, query_index


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


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


class Product(SearchableMixin, db.Model):
    __searchable__ = ['name', 'description']

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    sale_price = db.Column(db.Float)
    brand_id = db.Column(db.Integer,
                         db.ForeignKey('brand.id'),
                         nullable=False)
    category_id = db.Column(db.Integer,
                            db.ForeignKey('category.id'),
                            nullable=False)
    subcategory_id = db.Column(db.Integer,
                               db.ForeignKey('subcategory.id'),
                               nullable=False)

    category = db.relationship('Category', back_populates='products')
    subcategory = db.relationship('Subcategory', back_populates='products')
    brand = db.relationship('Brand', back_populates='products')
    product_variations = db.relationship('ProductVariation',
                                         back_populates='product')
    product_images = db.relationship('ProductImage', back_populates='product')

    def __repr__(self):
        return '<Product %r>' % self.name

    def create_product_variation(self, name):
        product_variation = ProductVariation(name=name, product_id=self.id)
        db.session.add(product_variation)
        return product_variation
    
    def create_product_image(self, image_url):
        product_image = ProductImage(image_url=image_url, product_id=self.id)
        db.session.add(product_image)
        return product_image


class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    product_id = db.Column(db.Integer,
                           db.ForeignKey('product.id'),
                           nullable=False)
    image_url = db.Column(db.String(255), nullable=False)

    product = db.relationship('Product', back_populates='product_images')

    def __repr__(self):
        return '<ProductImage %r>' % self.image_url


class ProductVariation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    product_id = db.Column(db.Integer,
                           db.ForeignKey('product.id'),
                           nullable=False)

    product_variation_values = db.relationship(
        'ProductVariationValue',
        back_populates='product_variation')
    product = db.relationship('Product', back_populates='product_variations')

    def __repr__(self):
        return '<ProductVariation %r>' % self.name

    def create_value(self, name):
        variant_value = ProductVariationValue(name=name,
                                              product_variation_id=self.id,
                                              product_id=self.product_id)
        db.session.add(variant_value)


class ProductVariationValue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    product_variation_id = db.Column(db.Integer,
                                     db.ForeignKey('product_variation.id'),
                                     nullable=False)
    product_id = db.Column(db.Integer,
                           db.ForeignKey('product.id'), 
                           nullable=False)

    product_variation = db.relationship(
        'ProductVariation',
        back_populates='product_variation_values')

    def __repr__(self):
        return '<ProductVariationValue %r>' % self.name


class WishlistProduct(db.Model):
    wishlist_id = db.Column(db.Integer, db.ForeignKey('wishlist.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)

    product = db.relationship('Product', lazy='joined')
    wishlist = db.relationship('Wishlist', back_populates='products')

    def __repr__(self):
        return '<WishlistProduct %r>' % self.product.name


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
    cart_products = db.relationship('CartProduct', back_populates='cart')

    def __repr__(self):
        return '<Cart %r>' % self.user.username

    @property
    def total_price(self):
        return sum(cp.total_price for cp in self.cart_products)

    def add_product(self, product, quantity=1,
                    product_variation_value_id=None):
        # Need to add self to session first
        db.session.add(self)
        for cp in self.cart_products:
            if cp.product == product:
                cp.quantity += quantity
                cp.total_price += (quantity * product.price)
                return
        # Select first product_variation value if none is selected
        if not product_variation_value_id and product.product_variations \
            and product.product_variations[0].values:
            product_variation_value_id = product.product_variations[0].values[0].id
        cp = CartProduct(
            cart=self,
            product=product,
            quantity=quantity,
            total_price=(quantity * product.price),
            product_variation_value_id=product_variation_value_id,
            total_sale_price=
                quantity * product.sale_price if product.sale_price else 0)
        db.session.add(cp)

    def remove_product(self, product):
        for cp in self.cart_products:
            if cp.product == product:
                self.cart_products.remove(cp)
                db.session.delete(cp)
                return
    
    def update_quantity(self, product, quantity):
        for cp in self.cart_products:
            if cp.product == product:
                if quantity == 0:
                    self.cart_products.remove(cp)
                    db.session.delete(cp)
                    return
                cp.quantity = quantity
                cp.total_price = quantity * product.price
                cp.total_sale_price = quantity * product.sale_price if product.sale_price else 0
                return

    def empty_cart(self):
        self.cart_products = []

    def cart_product_total_price(self, product):
        for cp in self.cart_products:
            if cp.product == product:
                return cp.total_price
        return 0

    def cart_product_total_sale_price(self, product):
        for cp in self.cart_products:
            if cp.product == product:
                return cp.total_sale_price
        return 0

    def cart_product_quantity(self, product):
        for cp in self.cart_products:
            if cp.product == product:
                return cp.quantity
        return 0


class CartProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, nullable=False, default=0)
    total_price = db.Column(db.Float, nullable=False, default=0.0)
    total_sale_price = db.Column(db.Float)
    product_variation_value_id = db.Column(
        db.Integer,
        db.ForeignKey('product_variation_value.id'))

    cart = db.relationship('Cart', back_populates='cart_products')
    product = db.relationship('Product', lazy='joined')
    product_variation_value = db.relationship('ProductVariationValue',
                                              lazy='joined')

    def __repr__(self):
        return '<CartProduct %r>' % self.product.name