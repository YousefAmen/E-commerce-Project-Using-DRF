from django.db import models
from django.utils.text import slugify
from accounts.models import UserProfile
import uuid


class Category(models.Model):
    name = models.CharField(max_length=500, default=None)
    slug = models.SlugField(null=True, blank=True, max_length=255)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Categorise"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/{self.slug}/"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class Product(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        default=1,
        related_name="products",
        verbose_name="Category",
    )
    name = models.CharField(
        max_length=1500,
        default=None,
        verbose_name="Product Name",
    )

    image = models.ImageField(
        upload_to="images/products_images/", verbose_name="Product Image", blank=True
    )
    description = models.TextField(default=None, null=True, blank=True)
    price = models.DecimalField(
        max_digits=8, decimal_places=2, default=0, verbose_name="Product Price"
    )
    discount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        null=True,
        blank=True,
        verbose_name="Dicount",
    )

    stock_quantity = models.IntegerField(default=1)
    favourites = models.ManyToManyField(
        UserProfile, blank=True, related_name="user_favourites"
    )
    slug = models.SlugField(null=True, blank=True, max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-date_added",)

    def __str__(self):
        return f"{self.user} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if self.discount:
            self.price -= self.discount
        return super().save(*args, **kwargs)


class ShippingAddress(models.Model):
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="shipping_addresses"
    )
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    address_line_1 = models.CharField("Address Line 1", max_length=255)
    address_line_2 = models.CharField(
        "Address Line 2", max_length=255, blank=True, null=True
    )
    city = models.CharField(max_length=100)
    state_or_province = models.CharField("State / Province", max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    shipping_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name}, {self.address_line_1}, {self.city}"


class Order(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=250)
    email = models.EmailField(max_length=255)
    shipped = models.BooleanField(default=False, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    date_shipped = models.DateTimeField(blank=True, null=True)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.CASCADE)
    stripe_session = models.CharField(max_length=255)

    def __str__(self):
        return f"Order-Email : {self.email}"


class OrderItem(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["order", "product"]

    def __str__(self):
        return f"{self.product.name}"

    @property
    def total_price(self):
        return self.quantity * self.price


class Comment(models.Model):
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="user_comments"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_comments"
    )
    body = models.TextField()
    active = models.BooleanField(default=True)
    slug = models.SlugField(null=True, blank=True, max_length=255, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} commented on {self.product.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.body)
        return super().save(*args, **kwargs)

    @property
    def comments_count(self):
        return self.product_comments.count()
