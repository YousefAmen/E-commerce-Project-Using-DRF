from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from store.models import Product
from .serializers import FavouriteSerializer


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def favourites(request, pk):
    """
    - Accept pk param for product
    - Accept only two methods :["POST","DELETE"]
    - Only Authenticated Users Can Added Product in Favourites
    """
    try:
        product = Product.objects.get(id=pk)
        if request.method == "POST":
            product.favourites.add(request.user)
            return Response(
                {"message": "Product Added to Favourites."}, status=status.HTTP_200_OK
            )
        else:
            product.favourites.remove(request.user)
            return Response(
                {"message": "Product removed to Favourites."}, status=status.HTTP_200_OK
            )
    except Product.DoesNotExist:

        return Response(
            {"message": "This product is not Exist."}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getUserFavourites(request):
    products = Product.objects.filter(favourites=request.user)
    serializer = FavouriteSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
