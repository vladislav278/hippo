from django.contrib import admin
from .models import Hospital


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    """Admin interface for Hospital model."""
    
    list_display = ['name', 'city', 'created_at']
    list_filter = ['city', 'created_at']
    search_fields = ['name', 'city', 'address']
    readonly_fields = ['created_at', 'updated_at']

