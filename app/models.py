from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    role = db.Column(db.String(64), default='user')
    password_hash = db.Column(db.String(128))

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