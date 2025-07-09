from django.urls import path
from .views import getCart, addItem, updateItem, removeItem

urlpatterns = [
    path("", getCart, name="add-item"),
    path("add-item/", addItem, name="add-item"),
    path("update-item/", updateItem, name="update-item"),
    path("remove-item/", removeItem, name="remove-item"),
]
