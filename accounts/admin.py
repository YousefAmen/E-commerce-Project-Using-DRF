from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile
from django.contrib.auth.forms import UserChangeForm, UserCreationForm


class UserProfileCreationForm(UserCreationForm):
    class Meta:
        model = UserProfile
        fields = ("email", "first_name", "last_name", "birthday", "gender", "avater")


class UserProfileChangeForm(UserChangeForm):
    class Meta:
        model = UserProfile
        fields = "__all__"


class UserProfileAdmin(UserAdmin):
    add_form = UserProfileCreationForm
    form = UserProfileChangeForm
    model = UserProfile
    list_display = ["first_name", "last_name", "is_active", "is_staff"]
    ordering = ("email",)
    search_fields = ["email", "first_name", "last_name"]
    readonly_fields = ("joined_at", "slug")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal Info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "gender",
                    "birthday",
                    "avater",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Dates", {"fields": ("last_login", "joined_at")}),
        ("SEO", {"fields": ("slug",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "gender",
                    "birthday",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )


admin.site.register(UserProfile, UserProfileAdmin)
