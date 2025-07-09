from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from .managers import UserProfileManager

GENDER_CHOICES = [("meal", "Meal"), ("femeal", "Femeal")]


class UserProfile(AbstractUser):
    username = None
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    gender = models.CharField(default=GENDER_CHOICES[0][0], choices=GENDER_CHOICES)
    avater = models.ImageField(upload_to="users/images/", blank=True, null=True)
    slug = models.SlugField(null=True, unique=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    objects = UserProfileManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "birthday"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            full_name = f"{self.first_name} {self.last_name}"
            self.slug = slugify(full_name)
        return super().save(*args, **kwargs)
