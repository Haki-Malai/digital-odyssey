from faker import Faker
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import User, Category, Subcategory, Brand, Product, Cart

fake = Faker()


def create_users(count=10):
    for i in range(count):
        user = User(
            username=fake.user_name(),
            email=fake.email(),
        )
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.commit()


def create_categories(count=5):
    for i in range(count):
        category = Category(name=fake.word())
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.commit()


def create_subcategories(count=5):
    categories = Category.query.all()
    for i in range(count):
        category = categories[fake.random_int(0, len(categories) - 1)]
        subcategory = Subcategory(name=fake.word(), category_id=category.id)
        db.session.add(subcategory)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.commit()


def create_brands(count=5):
    for i in range(count):
        brand = Brand(name=fake.word(), description=fake.sentence())
        db.session.add(brand)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.commit()


def create_products(count=10):
    brands = Brand.query.all()
    subcategories = Subcategory.query.all()
    for i in range(count):
        brand = brands[fake.random_int(0, len(brands) - 1)]
        subcategory = subcategories[fake.random_int(0, len(subcategories) - 1)]
        product = Product(
            name=fake.word(),
            description=fake.sentence(),
            price=fake.random_int(100, 1000),
            sale_price=fake.random_int(1000, 2000) if fake.boolean() else None,
            category_id=subcategory.category_id,
            subcategory_id=subcategory.id,
            brand_id=brand.id,
        )
        db.session.add(product)
        try:
            db.session.commit()
            variation = product.create_variation(fake.word())
            db.session.commit()
            try:
                variation.create_value(fake.word())
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
        except IntegrityError:
            db.session.commit()


def create_fake_admin():
    user = User(
        username='asdf',
        email='asdf@asdf.gr',
        role='admin'
    )
    user.set_password('asdf')
    db.session.add(user)
    db.session.commit()
    user.add_to_cart(Product.query.first(), 1)
    user.add_to_wishlist(Product.query.first())
    db.session.commit()
         