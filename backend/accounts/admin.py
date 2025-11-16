from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'role', 'hospital', 'is_staff', 'is_superuser']
    list_filter = ['role', 'is_staff', 'is_superuser', 'hospital']
    search_fields = ['email', 'username']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('role', 'hospital')}),
    )
