from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from .models import Patient, MedicalRecord, PatientDoctorRelation
from .serializers import (
    PatientSerializer,
    MedicalRecordSerializer,
    MedicalRecordDetailSerializer,
    PatientDoctorRelationSerializer,
    PatientWithRecordsSerializer
)


class PatientListView(generics.ListCreateAPIView):
    """Список пациентов врача и создание нового пациента."""
    
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'middle_name', 'phone', 'email']
    ordering_fields = ['last_name', 'created_at', 'date_of_birth']
    ordering = ['last_name']
    
    def get_queryset(self):
        """Врач видит только своих пациентов."""
        user = self.request.user
        
        # Если супер-админ или админ больницы - показываем всех пациентов их больницы
        if user.role in ['superadmin', 'hospital_admin']:
            if user.hospital:
                return Patient.objects.filter(hospital=user.hospital)
            elif user.role == 'superadmin':
                return Patient.objects.all()
        
        # Обычный врач видит только своих пациентов
        patient_ids = PatientDoctorRelation.objects.filter(
            doctor=user,
            is_active=True
        ).values_list('patient_id', flat=True)
        
        return Patient.objects.filter(id__in=patient_ids)
    
    def perform_create(self, serializer):
        """При создании пациента автоматически создаем связь с врачом."""
        patient = serializer.save()
        
        # Автоматически создаем связь врач-пациент
        PatientDoctorRelation.objects.get_or_create(
            patient=patient,
            doctor=self.request.user,
            defaults={'is_active': True}
        )


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Детальная информация о пациенте."""
    
    serializer_class = PatientWithRecordsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Врач видит только своих пациентов."""
        user = self.request.user
        
        if user.role in ['superadmin', 'hospital_admin']:
            if user.hospital:
                return Patient.objects.filter(hospital=user.hospital)
            elif user.role == 'superadmin':
                return Patient.objects.all()
        
        patient_ids = PatientDoctorRelation.objects.filter(
            doctor=user,
            is_active=True
        ).values_list('patient_id', flat=True)
        
        return Patient.objects.filter(id__in=patient_ids)


class MedicalRecordListView(generics.ListCreateAPIView):
    """Список медицинских карточек врача."""
    
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['visit_date', 'created_at']
    ordering = ['-visit_date']
    
    def get_queryset(self):
        """Врач видит только карточки своих пациентов."""
        user = self.request.user
        patient_id = self.request.query_params.get('patient', None)
        
        # Базовый queryset - карточки, созданные этим врачом
        queryset = MedicalRecord.objects.filter(doctor=user)
        
        # Если указан конкретный пациент, фильтруем по нему
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        # Если админ - показываем все карточки пациентов их больницы
        if user.role in ['superadmin', 'hospital_admin']:
            if user.hospital:
                queryset = MedicalRecord.objects.filter(
                    patient__hospital=user.hospital
                )
                if patient_id:
                    queryset = queryset.filter(patient_id=patient_id)
            elif user.role == 'superadmin':
                queryset = MedicalRecord.objects.all()
                if patient_id:
                    queryset = queryset.filter(patient_id=patient_id)
        
        return queryset
    
    def perform_create(self, serializer):
        """Автоматически устанавливаем врача при создании."""
        serializer.save(doctor=self.request.user)


class MedicalRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Детальная информация о медицинской карточке."""
    
    serializer_class = MedicalRecordDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Врач видит только свои карточки."""
        user = self.request.user
        
        if user.role in ['superadmin', 'hospital_admin']:
            if user.hospital:
                return MedicalRecord.objects.filter(patient__hospital=user.hospital)
            elif user.role == 'superadmin':
                return MedicalRecord.objects.all()
        
        return MedicalRecord.objects.filter(doctor=user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_cabinet_view(request):
    """Главная страница кабинета врача - статистика и краткая информация."""
    
    user = request.user
    
    # Получаем количество пациентов
    if user.role in ['superadmin', 'hospital_admin']:
        if user.hospital:
            patients_count = Patient.objects.filter(hospital=user.hospital).count()
            records_count = MedicalRecord.objects.filter(patient__hospital=user.hospital).count()
        elif user.role == 'superadmin':
            patients_count = Patient.objects.count()
            records_count = MedicalRecord.objects.count()
        else:
            patients_count = 0
            records_count = 0
    else:
        patient_ids = PatientDoctorRelation.objects.filter(
            doctor=user,
            is_active=True
        ).values_list('patient_id', flat=True)
        patients_count = Patient.objects.filter(id__in=patient_ids).count()
        records_count = MedicalRecord.objects.filter(
            doctor=user
        ).count()
    
    # Последние 5 пациентов
    if user.role in ['superadmin', 'hospital_admin']:
        if user.hospital:
            recent_patients = Patient.objects.filter(
                hospital=user.hospital
            ).order_by('-created_at')[:5]
        elif user.role == 'superadmin':
            recent_patients = Patient.objects.all().order_by('-created_at')[:5]
        else:
            recent_patients = Patient.objects.none()
    else:
        patient_ids = PatientDoctorRelation.objects.filter(
            doctor=user,
            is_active=True
        ).values_list('patient_id', flat=True)
        recent_patients = Patient.objects.filter(
            id__in=patient_ids
        ).order_by('-created_at')[:5]
    
    # Последние 5 медицинских карточек
    if user.role in ['superadmin', 'hospital_admin']:
        if user.hospital:
            recent_records = MedicalRecord.objects.filter(
                patient__hospital=user.hospital
            ).order_by('-visit_date')[:5]
        elif user.role == 'superadmin':
            recent_records = MedicalRecord.objects.all().order_by('-visit_date')[:5]
        else:
            recent_records = MedicalRecord.objects.none()
    else:
        recent_records = MedicalRecord.objects.filter(
            doctor=user
        ).order_by('-visit_date')[:5]
    
    return Response({
        'doctor': {
            'id': user.id,
            'email': user.email,
            'role': user.role,
            'hospital': user.hospital.name if user.hospital else None,
        },
        'statistics': {
            'patients_count': patients_count,
            'records_count': records_count,
        },
        'recent_patients': PatientSerializer(recent_patients, many=True).data,
        'recent_records': MedicalRecordSerializer(recent_records, many=True).data,
    })
