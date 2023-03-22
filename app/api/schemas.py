from app import ma
from app.models import User, ProductVariation, ProductVariationValue, \
    Product, ProductImage, Cart, CartProduct, Wishlist, WishlistProduct


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        ordered = True

    id = ma.auto_field(load_only=True)
    username = ma.auto_field()
    email = ma.auto_field()
    role = ma.auto_field(dump_only=True)

    cart = ma.Nested('CartSchema', many=False)


class ProductSchema(ma.SQLAlchemySchema):
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
    class Meta:
        model = ProductImage
        ordered = True

    id = ma.auto_field(load_only=True)
    image_url = ma.auto_field()


class ProductVariationSchema(ma.SQLAlchemySchema):
    class Meta:
        model = ProductVariation
        ordered = True

    id = ma.auto_field(load_only=True)
    name = ma.auto_field()

    product_variation_values = ma.Nested('ProductVariationValueSchema', many=True)


class ProductVariationValueSchema(ma.SQLAlchemySchema):
    class Meta:
        model = ProductVariationValue
        ordered = True

    id = ma.auto_field(load_only=True)
    name = ma.auto_field()


class WishlistSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Wishlist
        ordered = True

    id = ma.auto_field(load_only=True)

    wishlist_products = ma.Nested('WishlistProductSchema', many=True)


class WishlistProductSchema(ma.SQLAlchemySchema):
    class Meta:
        model = WishlistProduct
        ordered = True

    product = ma.Nested('ProductSchema')


class CartSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Cart
        ordered = True

    id = ma.auto_field(load_only=True)
    user = ma.Nested('UserSchema',
                     only=('id', 'username', 'email'),
                     dump_only=True)

    cart_products = ma.Nested('CartProductSchema', many=True)


class CartProductSchema(ma.SQLAlchemySchema):
    class Meta:
        model = CartProduct
        ordered = True

    id = ma.auto_field(load_only=True)
    product_id = ma.auto_field()
    quantity = ma.auto_field()
    total_price = ma.auto_field(dump_only=True)
    total_sale_price = ma.auto_field(dump_only=True)

    product_variation_value = ma.Nested('ProductVariationValueSchema')
    product = ma.Nested('ProductSchema')
