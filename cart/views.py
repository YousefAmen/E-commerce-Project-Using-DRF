from django.shortcuts import render
from .serializers import CartSerializer
from .models import Cart, CartItem
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from store.models import Product
from rest_framework import status


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getCart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    serializer = CartSerializer(cart)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def addItem(request):
    cart, created = Cart.objects.get_or_create(user=request.user)

    product_slug = request.data.get("product_slug")
    if not product_slug:
        return Response({"error": "product slug is required."})
    try:
        product = Product.objects.get(slug=product_slug)
    except Product.DoesNotExist:
        return Response(
            {"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND
        )
    quantity = request.data.get("quantity")
    if int(quantity) > product.stock_quantity:
        return Response(
            {
                "error": f"Only {product.stock_quantity} item(s) available in stock. Please reduce your quantity."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    elif not quantity:
        return Response(
            {"error": "quantity must be greater than 0,please choose the quantity."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    cartItem, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if created:
        cartItem.quantity = int(quantity)
    else:
        cartItem.quantity += quantity
    cartItem.save()

    serializer = CartSerializer(cart)
    return Response(
        {"data": serializer.data, "message": "Product Is Added Successfully"},
        status=status.HTTP_200_OK,
    )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def updateItem(request, id):
    try:
        cart_item = CartItem.objects.get(id=id, cart__user=request.user)
        quantity = request.data.get("quantity")
        if int(quantity) > cart_item.product.stock_quantity:
            return Response(
                {
                    "error": f"Only {cart_item.product.stock_quantity} item(s) available in stock. Please reduce your quantity."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif not quantity:
            return Response(
                {
                    "error": "quantity must be greater than 0,please choose the quantity."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        cart_item.quantity = int(quantity)
        cart_item.save()
        serializer = CartSerializer(cart_item.cart)

        return Response(
            {"message": "Cart Item Updated", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    except CartItem.DoesNotExist:
        return Response(
            {"message": "This Cart Item Is Not Exit"},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def removeItem(request, id):
    try:
        cartItem = CartItem.objects.get(id=id, cart__user=request.user)
        cartItem.delete()
        serializer = CartSerializer(cartItem.cart)
        return Response({"message": "Cart Item Is Delete Successfully."})

    except CartItem.DoesNotExist:
        return Response(
            {"message": "This Cart Item Is Not Exit"},
            status=status.HTTP_400_BAD_REQUEST,
        )
