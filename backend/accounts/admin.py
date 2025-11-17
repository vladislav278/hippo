from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, RegistrationKey


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'role', 'hospital', 'is_staff', 'is_superuser']
    list_filter = ['role', 'is_staff', 'is_superuser', 'hospital']
    search_fields = ['email', 'username']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('role', 'hospital')}),
    )


@admin.register(RegistrationKey)
class RegistrationKeyAdmin(admin.ModelAdmin):
    list_display = ['key', 'is_used', 'created_by', 'created_at', 'used_by', 'used_at']
    list_filter = ['is_used', 'created_at', 'used_at']
    search_fields = ['key']
    readonly_fields = ['key', 'created_at', 'used_at']
    ordering = ['-created_at']
