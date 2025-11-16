from rest_framework import serializers
from .models import Patient, MedicalRecord, PatientDoctorRelation
from accounts.serializers import UserSerializer
from hospitals.serializers import HospitalSerializer


class PatientSerializer(serializers.ModelSerializer):
    """Сериализатор для пациента."""
    
    full_name = serializers.CharField(read_only=True)
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)
    
    class Meta:
        model = Patient
        fields = ['id', 'first_name', 'last_name', 'middle_name', 'full_name', 
                  'date_of_birth', 'gender', 'phone', 'email', 'address', 
                  'hospital', 'hospital_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class MedicalRecordSerializer(serializers.ModelSerializer):
    """Сериализатор для медицинской карточки."""
    
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    doctor_email = serializers.CharField(source='doctor.email', read_only=True)
    
    class Meta:
        model = MedicalRecord
        fields = ['id', 'patient', 'patient_name', 'doctor', 'doctor_email',
                  'chief_complaint', 'diagnosis', 'anamnesis', 'allergies',
                  'chronic_diseases', 'current_medications', 'notes', 'visit_date',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'doctor', 'created_at', 'updated_at']


class MedicalRecordDetailSerializer(serializers.ModelSerializer):
    """Детальный сериализатор для медицинской карточки."""
    
    patient = PatientSerializer(read_only=True)
    doctor = UserSerializer(read_only=True)
    
    class Meta:
        model = MedicalRecord
        fields = ['id', 'patient', 'doctor', 'chief_complaint', 'diagnosis',
                  'anamnesis', 'allergies', 'chronic_diseases', 'current_medications',
                  'notes', 'visit_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PatientWithRecordsSerializer(serializers.ModelSerializer):
    """Сериализатор для пациента со всеми его карточками."""
    
    full_name = serializers.CharField(read_only=True)
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)
    medical_records = MedicalRecordSerializer(many=True, read_only=True)
    
    class Meta:
        model = Patient
        fields = ['id', 'first_name', 'last_name', 'middle_name', 'full_name',
                  'date_of_birth', 'gender', 'phone', 'email', 'address',
                  'hospital', 'hospital_name', 'medical_records', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

