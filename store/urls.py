from django.urls import path, include
from .views import (
    ProductViewset,
    CategoryViewset,
    OrderItemViewset,
    OrderViewset,
    ShippingAddressViewset,
    userOrdersPage,
    create_checkout_session,
    verify_payment,
    CommentsViewset,
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("product", ProductViewset, basename="product")
router.register("category", CategoryViewset, basename="category")
router.register("order", OrderViewset, basename="order")
router.register("order-item", OrderItemViewset, basename="order-item")
router.register("shipping-address", ShippingAddressViewset, basename="shipping-address")
router.register("comment", CommentsViewset, basename="comment")
urlpatterns = [
    path("", include(router.urls)),
    path("checkout/", create_checkout_session, name="checkout"),
    path("verify_payment/", verify_payment, name="verify_payment"),
    path("user-orders-page/", userOrdersPage, name="user-orders-page"),
]
