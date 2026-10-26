from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Notification


class CustomUserAdmin(UserAdmin):
    list_display = ["username", "email", "role", "credits", "is_active"]
    fieldsets = UserAdmin.fieldsets + (
        ("SkillShare", {"fields": ("role", "bio", "location", "photo", "credits")}),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Notification)

