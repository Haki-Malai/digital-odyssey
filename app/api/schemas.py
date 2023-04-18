from app import ma
from app.models import User, ProductVariation, ProductVariationValue, \
    Product, ProductImage, Cart, CartProduct, Wishlist, WishlistProduct


class EmptySchema(ma.Schema):
    """Empty schema.
    """
    pass


class UserSchema(ma.SQLAlchemySchema):
    """User schema.
    """
    class Meta:
        model = User
        ordered = True

    id = ma.auto_field(load_only=True)
    username = ma.auto_field()
    email = ma.auto_field()
    role = ma.auto_field(dump_only=True)

    cart = ma.Nested('CartSchema', many=False)


class ProductSchema(ma.SQLAlchemySchema):
    """Product schema.
    """
    class Meta:
        model = Product
        ordered = True

    id = ma.auto_field(load_only=True)
    name = ma.auto_field()
    description = ma.auto_field()
    price = ma.auto_field()
    sale_price = ma.auto_field()
    brand_id = ma.auto_field()
    category_id = ma.auto_field()
    subcategory_id = ma.auto_field()

    product_variations = ma.Nested('ProductVariationSchema', many=True)
    images = ma.Nested('ProductImageSchema', many=True)


class ProductImageSchema(ma.SQLAlchemySchema):
    """Product image schema.
    """
    class Meta:
        model = ProductImage
        ordered = True

    id = ma.auto_field(load_only=True)
    image_url = ma.auto_field()


class ProductVariationSchema(ma.SQLAlchemySchema):
    """Product variation schema.
    """
    class Meta:
        model = ProductVariation
        ordered = True

    id = ma.auto_field(load_only=True)
    name = ma.auto_field()

    product_variation_values = ma.Nested('ProductVariationValueSchema', many=True)


class ProductVariationValueSchema(ma.SQLAlchemySchema):
    """Product variation value schema.
    """
    class Meta:
        model = ProductVariationValue
        ordered = True

    id = ma.auto_field(load_only=True)
    name = ma.auto_field()


class WishlistSchema(ma.SQLAlchemySchema):
    """Wishlist schema.
    """
    class Meta:
        model = Wishlist
        ordered = True

    id = ma.auto_field(load_only=True)

    wishlist_products = ma.Nested('WishlistProductSchema', many=True)


class WishlistProductSchema(ma.SQLAlchemySchema):
    """Wishlist product schema.
    """
    class Meta:
        model = WishlistProduct
        ordered = True

    product = ma.Nested('ProductSchema')


class CartSchema(ma.SQLAlchemySchema):
    """Cart schema.
    """
    class Meta:
        model = Cart
        ordered = True

    id = ma.auto_field(load_only=True)
    total_price = ma.Float(dump_only=True)
    quantity = ma.Integer(dump_only=True)

    cart_products = ma.Nested('CartProductSchema', many=True)


class CartProductSchema(ma.SQLAlchemySchema):
    """Cart product schema.
    """
    class Meta:
        model = CartProduct
        ordered = True

    id = ma.auto_field(load_only=True)
    product_id = ma.auto_field()
    quantity = ma.auto_field()
    total_price = ma.auto_field(dump_only=True)

    product_variation_value = ma.Nested('ProductVariationValueSchema')
    product = ma.Nested('ProductSchema')
