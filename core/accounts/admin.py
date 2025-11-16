from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model."""
    
    list_display = ['email', 'username', 'role', 'hospital', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'hospital']
    search_fields = ['email', 'username']
    ordering = ['email']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('role', 'hospital')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Дополнительная информация', {'fields': ('role', 'hospital')}),
    )

