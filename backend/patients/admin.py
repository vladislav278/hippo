from django.contrib import admin
from .models import Patient, MedicalRecord, PatientDoctorRelation, Case, CaseMessage, MessageReaction


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


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ['patient', 'diagnosis', 'status', 'admission_date', 'created_by', 'created_at']
    search_fields = ['patient__first_name', 'patient__last_name', 'diagnosis']
    list_filter = ['status', 'admission_date', 'created_at']
    filter_horizontal = ['doctors']
    date_hierarchy = 'admission_date'


@admin.register(CaseMessage)
class CaseMessageAdmin(admin.ModelAdmin):
    list_display = ['case', 'author', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['content', 'author__email']


@admin.register(PatientDoctorRelation)
class PatientDoctorRelationAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'assigned_date', 'is_active']
    list_filter = ['is_active', 'assigned_date']
    search_fields = ['patient__first_name', 'patient__last_name', 'doctor__email']


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = ['message', 'user', 'reaction', 'created_at']
    list_filter = ['reaction', 'created_at']
    search_fields = ['user__email', 'message__content']
