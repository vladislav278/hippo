from rest_framework import serializers
from .models import Patient, MedicalRecord, PatientDoctorRelation
from accounts.serializers import UserSerializer
from hospitals.serializers import HospitalSerializer


class PatientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Patient."""
    
    full_name = serializers.CharField(read_only=True)
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)
    
    class Meta:
        model = Patient
        fields = [
            'id', 'first_name', 'last_name', 'middle_name', 'full_name',
            'date_of_birth', 'gender', 'phone', 'email', 'address',
            'hospital', 'hospital_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MedicalRecordSerializer(serializers.ModelSerializer):
    """Сериализатор для медицинской карточки."""
    
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.email', read_only=True)
    
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'patient', 'patient_name', 'doctor', 'doctor_name',
            'chief_complaint', 'diagnosis', 'anamnesis', 'allergies',
            'chronic_diseases', 'current_medications', 'notes',
            'visit_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'doctor']
    
    def create(self, validated_data):
        """Автоматически устанавливаем текущего врача при создании."""
        validated_data['doctor'] = self.context['request'].user
        return super().create(validated_data)


class MedicalRecordDetailSerializer(MedicalRecordSerializer):
    """Расширенный сериализатор с полной информацией о пациенте."""
    
    patient = PatientSerializer(read_only=True)
    doctor = UserSerializer(read_only=True)


class PatientDoctorRelationSerializer(serializers.ModelSerializer):
    """Сериализатор для связи врач-пациент."""
    
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.email', read_only=True)
    
    class Meta:
        model = PatientDoctorRelation
        fields = [
            'id', 'patient', 'patient_name', 'doctor', 'doctor_name',
            'assigned_date', 'is_active', 'notes'
        ]
        read_only_fields = ['id', 'assigned_date']


class PatientWithRecordsSerializer(PatientSerializer):
    """Сериализатор пациента с его медицинскими карточками."""
    
    medical_records = MedicalRecordSerializer(many=True, read_only=True)
    treating_doctors = serializers.SerializerMethodField()
    
    def get_treating_doctors(self, obj):
        """Получить список врачей, которые лечат этого пациента."""
        active_relations = obj.treating_doctors.filter(is_active=True)
        return [
            {
                'id': rel.doctor.id,
                'email': rel.doctor.email,
                'assigned_date': rel.assigned_date
            }
            for rel in active_relations
        ]

