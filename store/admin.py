from django.contrib import admin

from .models import Order, OrderItem, Product, Category, ShippingAddress, Comment


admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(Comment)
