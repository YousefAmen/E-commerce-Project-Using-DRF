from rest_framework import serializers

from accounts.serializers import UserProfileSerializer
from .models import Product, Category, Order, OrderItem, ShippingAddress, Comment


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ["name", "slug"]


class CommentsSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "email": obj.user.email,
            "avater": obj.user.avater.url if obj.user.avater else None,
            "joined_at": obj.user.joined_at,
            "slug": obj.user.slug,
        }

    class Meta:
        model = Comment
        fields = [
            "user",
            "product",
            "body",
            "comments_count",
            "slug",
            "created_at",
            "updated_at",
        ]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "image",
            "price",
            "stock_quantity",
            "category",
            "discount",
            "date_added",
            "slug",
        ]


class ProductRetrieveSerializer(serializers.ModelSerializer):
    """
    - it's used only when the action of the viewset is retrive to get the product comments
    - notice don't  used it when for all action it will give you error RecursionError: maximum recursion depth exceeded
    - because you try to get the all comments of all products and this is not iffecient way
    """

    category = CategorySerializer(read_only=True)
    product_comments = CommentsSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "image",
            "price",
            "stock_quantity",
            "category",
            "discount",
            "date_added",
            "product_comments",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source="product", read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "order",
            "product_details",
            "price",
            "total_price",
            "created_at",
            "quantity",
        ]


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "full_name",
            "email",
            "total_amount",
            "shipped",
            "paid",
            "created_at",
            "updated_at",
            "order_items",
        ]


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = [
            "full_name",
            "phone_number",
            "address_line_1",
            "address_line_2",
            "city",
            "state_or_province",
            "postal_code",
            "country",
            "is_default",
            "shipping_uuid",
            "created_at",
        ]
