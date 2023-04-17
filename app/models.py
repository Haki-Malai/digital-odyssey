from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin

from app import db, login
from app.search import add_to_index, remove_from_index, query_index


class SearchableMixin(object):
    """Mixin for adding search capabilities to SQLAlchemy models.
    """
    @classmethod
    def search(cls, expression, page, per_page):
        """Search the index for items that match the given expression.
        :param expression: the expression to search for
        :param page: the page number to return
        :param per_page: the number of items to return per page
        :return: a tuple containing the results and the total number of
        results
        """
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(*when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session) -> None:
        """Register objects to be indexed after the commit.
        :param session: the current session
        """
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session) -> None:
        """Index the registered objects.
        :param session: the current session
        """
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
    wishlist = db.relationship('Wishlist', back_populates='user',
                               uselist=False)

    def __repr__(self) -> str:
        return '<User %r>' % self.username

    def __init__(self, **kwargs):
        """Create a new user instance and add a cart and wishlist to it.
        """
        super(User, self).__init__(**kwargs)
        Cart(user=self)
        Wishlist(user=self)

    @property
    def password(self):
        """Prevent password from being accessed.
        """
        raise AttributeError('password is not a readable attribute')

    def set_password(self, password):
        """Set the password for the user.
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Check if the password is correct.
        """
        return check_password_hash(self.password_hash, password)

    def has_permission(self, permission):
        """Check if the user has the given permission.
        """
        return self.role == permission

    def add_to_cart(self, product, quantity):
        """Add a product to the user's cart.
        """
        if not self.cart:
            self.cart = Cart(user=self)
        self.cart.add_product(product, quantity)

    def remove_from_cart(self, product):
        """Remove a product from the user's cart.
        """
        if self.cart:
            self.cart.remove_product(product)

    def empty_cart(self):
        """Empty the user's cart.
        """
        if self.cart:
            self.cart.empty_cart()

    def add_to_wishlist(self, product):
        """Add a product to the user's wishlist.
        """
        if not self.wishlist:
            self.wishlist = Wishlist(user=self)
        self.wishlist.add_product(product)

    def remove_from_wishlist(self, product):
        """Remove a product from the user's wishlist.
        """
        if product in self.wishlist:
            self.wishlist.remove(product)

    def add_to_cart(self, product_id, quantity=1):
        """Add a product to the user's cart.
        """
        return self.cart.add_product(product_id, quantity)

    def remove_from_cart(self, product_id):
        """Remove a product from the user's cart.
        """
        if self.cart:
            self.cart.remove_product(product_id)


class AnonymousUser(AnonymousUserMixin):
    """Anonymous user class.
    """
    def has_permission(self, permission):
        """Return False for all permissions."""
        return False

    def is_administrator(self):
        """Return False."""
        return False

login.anonymous_user = AnonymousUser


@login.user_loader
def load_user(id):
    """Load a user from the database.
    """
    return User.query.get(int(id))


class Category(db.Model):
    """Category model.
    """
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(64), unique=True, index=True)

    subcategories = db.relationship('Subcategory', back_populates='category')
    products = db.relationship('Product', back_populates='category')

    def __repr__(self):
        return '<Category %r>' % self.name


class Subcategory(db.Model):
    """Subcategory model.
    """
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(124), index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    category = db.relationship('Category', back_populates='subcategories')
    products = db.relationship('Product', back_populates='subcategory')

    def __repr__(self):
        return '<Subcategory %r>' % self.name


class Brand(db.Model):
    """Brand model.
    """
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)

    products = db.relationship('Product', back_populates='brand')

    def __repr__(self):
        return '<Brand %r>' % self.name


class Product(SearchableMixin, db.Model):
    """Product model.
    """
    __searchable__ = ['name', 'description']

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    sale_price = db.Column(db.Float)
    featured = db.Column(db.Boolean, default=False)
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
    variations = db.relationship('ProductVariation', back_populates='product',
                                 lazy='dynamic')
    images = db.relationship('ProductImage', back_populates='product',
                             lazy='dynamic')

    def __repr__(self):
        return '<Product %r>' % self.name

    def __init__(self, **kwargs):
        """Create a new product instance with a default image and
        default variation.
        """
        super(Product, self).__init__(**kwargs)
        ProductImage(product=self, image_url='uploads/product/default.png')
        ProductVariation(product=self, name='Variation')


class ProductImage(db.Model):
    """Product image model."""
    id = db.Column(db.Integer, primary_key=True, index=True)
    product_id = db.Column(db.Integer,
                           db.ForeignKey('product.id'),
                           nullable=False)
    image_url = db.Column(db.String(255), nullable=False)

    product = db.relationship('Product', back_populates='images')

    def __repr__(self):
        return '<ProductImage %r>' % self.image_url


class ProductVariation(db.Model):
    """Product variation model.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    product_id = db.Column(db.Integer,
                           db.ForeignKey('product.id'),
                           nullable=False)

    values = db.relationship('ProductVariationValue',
                             back_populates='variation',
                             lazy='dynamic')
    product = db.relationship('Product', back_populates='variations')

    def __repr__(self):
        return '<ProductVariation %r>' % self.name

    def __init__(self, **kwargs):
        super(ProductVariation, self).__init__(**kwargs)
        ProductVariationValue(variation=self,
                              product=self.product,
                              name='Default')


class ProductVariationValue(db.Model):
    """Product variation value model.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    variation_id = db.Column(db.Integer,
                             db.ForeignKey('product_variation.id'),
                             nullable=False)
    product_id = db.Column(db.Integer,
                           db.ForeignKey('product.id'),
                           nullable=False)

    variation = db.relationship('ProductVariation',
                                back_populates='values')
    product = db.relationship('Product')

    def __repr__(self):
        return '<ProductVariationValue %r>' % self.name


class Wishlist(db.Model):
    """Wishlist model.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship('User', back_populates='wishlist')
    products = db.relationship('WishlistProduct', back_populates='wishlist')

    def __repr__(self):
        return '<Wishlist %r>' % self.user.username

    @property
    def quantity(self):
        return len(self.products)

    def add_product(self, product_id):
        wishlist_product = WishlistProduct(wishlist=self,
                                           product_id=product_id)
        db.session.add(wishlist_product)


class WishlistProduct(db.Model):
    """Wishlist product model.
    """
    wishlist_id = db.Column(db.Integer, db.ForeignKey('wishlist.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)

    product = db.relationship('Product', lazy='joined')
    wishlist = db.relationship('Wishlist', back_populates='products')

    def __repr__(self):
        return '<WishlistProduct %r>' % self.product.name


class Cart(db.Model):
    """Cart model.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship('User', back_populates='cart')
    cart_products = db.relationship('CartProduct',
                                    back_populates='cart',
                                    lazy='dynamic')

    def __repr__(self):
        return '<Cart %r>' % self.user.username

    @property
    def total_price(self):
        """Return the total price of all products in the cart.
        """
        return sum(cp.total_price for cp in self.cart_products)

    @property
    def quantity(self):
        """Return the total quantity of all products in the cart.
        """
        return self.cart_products.count()

    def add_product(self, product_id, quantity=1, product_value_id=None):
        """Add a product to the cart.
        :param product_id: The id of the product to add.
        :param quantity: The quantity of the product to add.
        :param product_value_id: The id of the product variation value.
        """
        product = Product.query.get(product_id)
        if not product:
            return False
        if quantity < 1:
            self.remove_product(product_id)
            return True
        for cart_product in self.cart_products:
            if cart_product.product == product:
                cart_product.quantity = quantity
                cart_product.total_price = quantity * product.price
                db.session.add(cart_product)
                db.session.commit()
                return True
        # Select first variation value if none is selected
        if not product_value_id:
            product_value_id = product.variations.first().values.first().id
        cart_product = CartProduct(
            cart=self,
            product=product,
            quantity=quantity,
            total_price=quantity * product.price,
            value_id=product_value_id)
        db.session.add(cart_product)
        db.session.commit()
        return True

    def remove_product(self, product_id):
        """Remove a product from the cart.
        :param product_id: The id of the product to remove.
        """
        for cart_product in self.cart_products:
            if cart_product.product_id == product_id:
                self.cart_products.remove(cart_product)
                db.session.delete(cart_product)
                db.session.commit()
                return

    def empty_cart(self):
        """Empty the cart.
        """
        for cart_product in self.cart_products:
            self.cart_products.remove(cart_product)
            db.session.delete(cart_product)
            return

    def has_product(self, product_id):
        """Check if the cart has a product.
        """
        for cart_product in self.cart_products:
            if cart_product.product_id == product_id:
                return True
        return False


class CartProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, nullable=False, default=0)
    total_price = db.Column(db.Float, nullable=False, default=0.0)
    value_id = db.Column(db.Integer,
                         db.ForeignKey('product_variation_value.id'))

    cart = db.relationship('Cart', back_populates='cart_products')
    product = db.relationship('Product', lazy='joined')
    value = db.relationship('ProductVariationValue', lazy='joined')

    def __repr__(self):
        return '<CartProduct %r>' % self.product.name


class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    image_url = db.Column(db.String(255), nullable=False,
                          default='uploads/banner/default.png')
    url = db.Column(db.String(255), nullable=False, default='main.products')
    name = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    button_text = db.Column(db.String(255), nullable=False,
                            default='Shop Now')
    position = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return '<Banner %r>' % self.name
