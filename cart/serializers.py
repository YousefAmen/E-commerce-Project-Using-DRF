from store.models import Product
from .models import Cart, CartItem
from rest_framework import serializers
from store.serializers import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity"]


class CartSerializer(serializers.ModelSerializer):
    cartItem = CartItemSerializer(source="items", read_only=True, many=True)

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "cartItem",
            "num_of_items",
            "total_price",
            "created_at",
            "modified_at",
        ]
