from django.contrib import admin
from .models import Patient, MedicalRecord, PatientDoctorRelation


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    """Админка для модели Patient."""
    
    list_display = ['full_name', 'date_of_birth', 'gender', 'phone', 'hospital', 'created_at']
    list_filter = ['gender', 'hospital', 'created_at']
    search_fields = ['first_name', 'last_name', 'middle_name', 'phone', 'email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('first_name', 'last_name', 'middle_name', 'date_of_birth', 'gender')
        }),
        ('Контакты', {
            'fields': ('phone', 'email', 'address')
        }),
        ('Дополнительно', {
            'fields': ('hospital', 'created_at', 'updated_at')
        }),
    )


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    """Админка для медицинских карточек."""
    
    list_display = ['patient', 'doctor', 'diagnosis', 'visit_date', 'created_at']
    list_filter = ['visit_date', 'created_at', 'doctor']
    search_fields = ['patient__first_name', 'patient__last_name', 'diagnosis', 'chief_complaint']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Пациент и врач', {
            'fields': ('patient', 'doctor', 'visit_date')
        }),
        ('Медицинская информация', {
            'fields': ('chief_complaint', 'diagnosis', 'anamnesis')
        }),
        ('Дополнительная информация', {
            'fields': ('allergies', 'chronic_diseases', 'current_medications', 'notes')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(PatientDoctorRelation)
class PatientDoctorRelationAdmin(admin.ModelAdmin):
    """Админка для связи врач-пациент."""
    
    list_display = ['patient', 'doctor', 'assigned_date', 'is_active']
    list_filter = ['is_active', 'assigned_date', 'doctor']
    search_fields = ['patient__first_name', 'patient__last_name', 'doctor__email']
    readonly_fields = ['assigned_date']
