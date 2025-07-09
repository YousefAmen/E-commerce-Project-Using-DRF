from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework import status
import stripe.error

from cart.models import Cart, CartItem
from .models import Order, OrderItem, Product, Category, ShippingAddress, Comment
from .serializers import (
    CommentsSerializer,
    OrderItemSerializer,
    OrderSerializer,
    ProductRetrieveSerializer,
    ProductSerializer,
    CategorySerializer,
    ShippingAddressSerializer,
)
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    AllowAny,
)
from rest_framework.decorators import (
    action,
    authentication_classes,
    permission_classes,
    api_view,
    APIView,
)
from django.db.models import Q
from .permissions import IsOrderItemOwner, IsOwner
from rest_framework.exceptions import PermissionDenied
from cart.serializers import CartItemSerializer, CartSerializer
from django.db import transaction
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


# Start CRUD On Category Using FBV

# @api_view(["GET"])
# @permission_classes([IsAuthenticatedOrReadOnly])
# def getCategories(request):
#     categories = Category.objects.all()
#     serializer = CategorySerializer(categories, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)


# @api_view(["POST"])
# @permission_classes([IsAdminUser])
# def createCategory(request):
#     serializer = CategorySerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.user = request.user
#         serializer.save()
#         return Response(
#             {"message": "Category Added Successfully."}, status=status.HTTP_201_CREATED
#         )
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(["PUT"])
# @permission_classes([IsAdminUser])
# def updateCategory(request, slug):
#     try:
#         category = Category.objects.get(slug=slug)
#     except Category.DoesNotExist:
#         return Response(
#             {"message": "This Category Is Not Exist."}, status=status.HTTP_404_NOT_FOUND
#         )
#     serializer = CategorySerializer(category)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(
#             {"message": "Category Updated Successfully."}, status=status.HTTP_200_OK
#         )
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(["DELETE"])
# @permission_classes([IsAdminUser])
# def DestroyCategory(request, slug):
#     try:
#         category = Category.objects.get(slug=slug)
#     except Category.DoesNotExist:
#         return Response(
#             {"message": "This Category Is Not Exist."}, status=status.HTTP_404_NOT_FOUND
#         )
#     category.delete()
#     return Response(
#         {"message": "Category Deleted Successfully."}, status=status.HTTP_204_NO_CONTENT
#     )


# # Start CRUD On Product Using FBV


# @api_view(["GET"])
# @permission_classes([IsAuthenticatedOrReadOnly])
# def getProducts(request):
#     products = Product.objects.all()
#     serializer = ProductSerializer(products, many=True)
#     return Response(serializer.data)


# @api_view(["POST"])
# @permission_classes([IsAdminUser])
# def createProducts(request):
#     serializer = ProductSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.user = request.user
#         serializer.save()
#         return Response(
#             {"message": "Product Added Successfully."}, status=status.HTTP_201_CREATED
#         )
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(["PUT"])
# @permission_classes([IsAdminUser])
# def updateProduct(request, slug):
#     try:
#         product = Product.objects.get(slug=slug)
#     except Product.DoesNotExist:
#         return Response(
#             {"message": "This Product Is Not Exist."}, status=status.HTTP_404_NOT_FOUND
#         )
#     serializer = ProductSerializer(product)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(
#             {"message": "Product Updated Successfully."}, status=status.HTTP_200_OK
#         )
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(["DELETE"])
# @permission_classes([IsAdminUser])
# def DestroyProduct(request, slug):
#     try:
#         product = Product.objects.get(slug=slug)
#     except Product.DoesNotExist:
#         return Response(
#             {"message": "This Product Is Not Exist."}, status=status.HTTP_404_NOT_FOUND
#         )
#     product.delete()
#     return Response(
#         {"message": "Product Deleted Successfully."}, status=status.HTTP_204_NO_CONTENT
#     )


# @api_view(["GET"])
# def product_search(request):
#     search_term = request.query_params.get("search_term")
#     if search_term:
#         products = Product.objects.filter(
#             Q(name__icontains=search_term) | Q(discription__icontains=search_term)
#         )
#         if products:
#             serailizer = ProductSerializer(products, many=True)
#             return Response(serailizer.data, status=status.HTTP_200_OK)
#         return Response(
#             {"message": f"No Product Matches This Search {search_term}"},
#             status=status.HTTP_200_OK,
#         )
#     return Response(status=status.HTTP_400_BAD_REQUEST)


class ProductViewset(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "discription"]
    ordering_fields = ["price", "date_added"]
    lookup_field = "slug"

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductRetrieveSerializer
        return ProductSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryViewset(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    lookup_field = "slug"

    @action(detail=True, methods=["get"])
    def products(self, request, slug=None):
        category = self.get_object()
        products = Product.objects.filter(category=category)
        serializer = ProductSerializer(products, many=True)

        return Response(serializer.data)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return [AllowAny()]


class OrderViewset(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    lookup_field = "order_uuid"
    ordering_fields = ["created_at", "updated_at", "amount"]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderItemViewset(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated, IsOrderItemOwner]
    ordering_fields = ["price"]

    def get_queryset(self):
        return OrderItem.objects.filter(order__user=self.request.user)


class ShippingAddressViewset(viewsets.ModelViewSet):
    queryset = ShippingAddress.objects.all()
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "shipping_uuid"

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentsViewset(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentsSerializer
    ordering = ["created_at", "updated_at"]
    permission_classes = [IsAuthenticated]
    lookup_field = "slug"

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user, active=True)

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsOwner])
def create_checkout_session(request):
    try:

        cart = Cart.objects.get(user=request.user)
        if not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        line_items = []
        # check if item quantity is not dealing with the item product quantity
        for item in cart.items.all():
            if item.quantity > item.product.stock_quantity:
                return Response(
                    {
                        "error": f"Only {item.product.stock_quantity} item(s) available in stock. Please reduce your quantity."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if item.quantity == 0:
                return Response(
                    {
                        "error": f"The quantity for '{item.product.name}' cannot be zero. Please set at least 1 item."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            line_items.append(
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": item.product.name,
                            "description": item.product.description,
                        },
                        "unit_amount": int(item.product.price * 100),
                    },
                    "quantity": item.quantity,
                }
            )
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=request.build_absolute_uri(
                "payment/success/?session_id={CHECKOUT_SESSION_ID}"
            ),
            cancel_url=request.build_absolute_uri(("payment/cancel/")),
            metadata={
                "user_id": request.user.id,
                "cart_id": cart.id,
                "user_email": request.user.email,
            },
            customer_email=request.user.email,
        )
        return Response(
            {
                "checkout": session.url,
                "session_id": session.id,
            },
            status=status.HTTP_200_OK,
        )

    except Cart.DoesNotExist:

        return Response(
            {"message": "your cart is empty."}, status=status.HTTP_400_BAD_REQUEST
        )
    except stripe.error.StripeError as e:
        return Response(
            {"error": f"Stripe error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def verify_payment(request):
    session_id = request.query_params.get("session_id")
    session = stripe.checkout.Session.retrieve(session_id)
    if session.payment_status != "paid":
        return Response(
            {"error": "Payment was not successfull."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    # get the user id and the cart id from metadata that i will already send it in the create session
    user_id = session.metadata.get("user_id")
    cart_id = session.metadata.get("cart_id")
    if str(request.user.id) != user_id:
        return Response(
            {"error": "Payment doesn't belong to this user"},
            status=status.HTTP_403_FORBIDDEN,
        )
    # check if if the order is already exists and the paid of it is false
    existing_order = Order.objects.filter(
        user=user_id, stripe_session=session_id, paid=True
    ).first()
    # pervent duplicating orders
    if existing_order:
        serializer = OrderSerializer(existing_order)
        return Response(
            {"message": "This order is already exists", "ordre": serializer.data},
            status=status.HTTP_200_OK,
        )
    # get the cart of the user
    cart = Cart.objects.get(id=cart_id, user=request.user)

    try:
        with transaction.atomic():
            shipping_address = ShippingAddress.objects.filter(
                user=cart.user, is_default=True
            ).first()
            if not shipping_address:
                return Response(
                    {
                        "error": "Shipping address is required. Please add one before checkout."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            order = Order.objects.create(
                user=cart.user,
                full_name=f"{cart.user.first_name} {cart.user.last_name}",
                email=cart.user.email,
                total_amount=cart.total_price(),
                shipping_address=shipping_address,
                stripe_session=session_id,
                paid=True,
            )
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price,
                )
                # manage the stock
                item.product.stock_quantity -= item.quantity
                item.product.save()
            cart.delete()
            serializer = OrderSerializer(order)
            return Response(
                {"message": "Order Created Successfully.", "order": serializer.data},
                status=status.HTTP_200_OK,
            )
    except ShippingAddress.DoesNotExist:
        return Response(
            {"message": "Sorry, you don't have a shipping address please add one."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Cart.DoesNotExist:
        return Response(
            {"message": "cart is not found"}, status=status.HTTP_400_BAD_REQUEST
        )
    except stripe.error.StripeError as e:
        return Response(
            {"error": f"Stripe error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsOwner])
def userOrdersPage(request):
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
