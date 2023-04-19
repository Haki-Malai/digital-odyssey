from faker import Faker
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import User, Category, Subcategory, Brand, Product, Banner

fake = Faker()


def create_users(count: int = 10) -> None:
    """Create fake users.
    :param count: Number of users to create.
    """
    i = 0
    while i < count:
        user = User(
            username=fake.user_name(),
            email=fake.email(),
        )
        db.session.add(user)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def create_categories(count: int = 5) -> None:
    """Create fake categories.
    :param count: Number of categories to create.
    """
    i = 0
    while i < count:
        category = Category(name=fake.word())
        db.session.add(category)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def create_subcategories(count: int = 5) -> None:
    """Create fake subcategories.
    :param count: Number of subcategories to create.
    """
    i = 0
    categories = Category.query.all()
    while i < count:
        category = categories[fake.random_int(0, len(categories) - 1)]
        subcategory = Subcategory(name=fake.word(), category_id=category.id)
        db.session.add(subcategory)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def create_brands(count: int = 5) -> None:
    """Create fake brands.
    :param count: Number of brands to create.
    """
    i = 0
    while i < count:
        brand = Brand(name=fake.word(), description=fake.sentence())
        db.session.add(brand)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def create_products(count: int = 10) -> None:
    """Create fake products.
    :param count: Number of products to create.
    """
    i = 0
    brands = Brand.query.all()
    subcategories = Subcategory.query.all()
    while i < count:
        brand = brands[fake.random_int(0, len(brands) - 1)]
        subcategory = subcategories[fake.random_int(0, len(subcategories) - 1)]
        product = Product(
            name=fake.word(),
            description=fake.sentence(),
            price=fake.random_int(100, 1000),
            sale_price=fake.random_int(1000, 2000) if fake.boolean() else None,
            featured=fake.boolean(),
            category_id=subcategory.category_id,
            subcategory_id=subcategory.id,
            brand_id=brand.id,
        )
        db.session.add(product)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def create_fake_banners(count: int = 5) -> None:
    """Create fake banners.
    :param count: Number of banners to create.
    """
    banner1 = Banner(
        name=fake.word(),
        body=fake.sentence(),
        position=1)
    banner2 = Banner(
        name=fake.word(),
        body=fake.sentence(),
        position=2)
    banner3 = Banner(
        name=fake.word(),
        body=fake.sentence(),
        position=3)
    db.session.add_all([banner1, banner2, banner3])
    db.session.commit()

    i = 0
    while i < count:
        banner = Banner(
            name=fake.word(),
            body=fake.sentence(),
        )
        db.session.add(banner)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def create_fake_admin() -> None:
    """Create fake admin user.
    """
    try:
        user = User(
            username='asdf',
            email='asdf@asdf.gr',
            role='admin'
        )
        user.set_password('asdf')
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return
