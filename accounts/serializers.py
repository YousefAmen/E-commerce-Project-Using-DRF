from rest_framework import serializers
from .models import UserProfile
from djoser.serializers import UserSerializer, UserCreateSerializer
from store.models import Product


class FavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name"]


class UserProfileSerializer(UserSerializer):
    favourites_products = FavouriteSerializer(
        source="user_favourites", many=True, read_only=True
    )

    user_orders = serializers.SerializerMethodField()

    def get_user_orders(self, obj):
        from store.serializers import OrderSerializer

        orders = obj.order_set.all()
        return OrderSerializer(orders, many=True, context=self.context).data

    class Meta:
        model = UserProfile
        fields = [
            "first_name",
            "last_name",
            "email",
            "avater",
            "joined_at",
            "slug",
            "favourites_products",
            "user_orders",
        ]


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = UserProfile
        fields = ("id", "first_name", "last_name", "email", "birthday", "password")
