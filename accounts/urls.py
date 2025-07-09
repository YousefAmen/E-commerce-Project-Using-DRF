from django.urls import path
from .views import favourites, getUserFavourites

urlpatterns = [
    path("favourites/<int:pk>/", favourites, name="favourites"),
    path("user_favourites/", getUserFavourites, name="get-user-favourites"),
]
