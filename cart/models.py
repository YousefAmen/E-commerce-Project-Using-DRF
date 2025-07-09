from django.db import models
from store.models import Product
from accounts.models import UserProfile


class Cart(models.Model):
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="carts"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart({self.id}) - User({self.user.email})"

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def num_of_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self):
        return f" {self.quantity} {self.product.name}"

    def total_price(self):
        return self.product.price * self.quantity
