from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("phone", "is_verified", "is_staff", "is_active", "is_host")
    list_filter = ("phone", "is_verified", "is_staff", "is_active", "is_host")
    searching_fields = ("phone", "email")
    ordering = ("phone", "is_host")
    filter_horizontal = ("groups", "user_permissions")

    fieldsets = (
        (
            "authentication",
            {
                "fields": ("phone", "name", "email", "password"),
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_host",
                    "is_verified",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "user_permissions",
                    "groups",
                )
            },
        ),
        ("Important dates", {"fields": ("date_joined",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "phone",
                    "email",
                    "name",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "is_host",
                ),
            },
        ),
    )


admin.site.register(User, CustomUserAdmin)
