from django.contrib import admin

# Register your models here.

from .models import User
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'user_type', 'first_name', 'last_name', 'phone_number', 'is_active', 'created_at', 'updated_at')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('user_type', 'is_active')