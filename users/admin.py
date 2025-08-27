from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

# Register your models here.
@admin.register(User)
class UserAdmin(BaseUserAdmin):

    fieldsets = BaseUserAdmin.fieldsets + ((_("Role"), {"fields": ("role",)}),)
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {"classes": ("wide",), "fields": ("username", "password1", "password2", "role")}),
    )
    search_fields = ("username", "email")
    ordering = ("username",)
