from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin


User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("email", "is_staff")
    list_display_links = ("email", )
    search_fields = ("email", )
