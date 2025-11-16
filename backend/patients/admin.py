from django.contrib import admin
from .models import Patient, MedicalRecord, PatientDoctorRelation


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'date_of_birth', 'gender', 'hospital', 'created_at']
    search_fields = ['first_name', 'last_name', 'middle_name', 'phone', 'email']
    list_filter = ['gender', 'hospital', 'created_at']
    date_hierarchy = 'date_of_birth'


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'visit_date', 'diagnosis', 'created_at']
    search_fields = ['patient__first_name', 'patient__last_name', 'doctor__email', 'diagnosis']
    list_filter = ['visit_date', 'created_at']
    date_hierarchy = 'visit_date'


@admin.register(PatientDoctorRelation)
class PatientDoctorRelationAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'assigned_date', 'is_active']
    list_filter = ['is_active', 'assigned_date']
    search_fields = ['patient__first_name', 'patient__last_name', 'doctor__email']
