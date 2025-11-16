from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from .models import Patient, MedicalRecord, PatientDoctorRelation
from .serializers import (
    PatientSerializer, PatientWithRecordsSerializer,
    MedicalRecordSerializer, MedicalRecordDetailSerializer
)


def get_patient_queryset(user):
    """Получить queryset пациентов в зависимости от роли пользователя."""
    if user.role == 'superadmin':
        return Patient.objects.all()
    elif user.role == 'hospital_admin':
        return Patient.objects.filter(hospital=user.hospital)
    else:  # doctor
        return Patient.objects.filter(
            treating_doctors__doctor=user,
            treating_doctors__is_active=True
        ).distinct()


def get_medical_record_queryset(user):
    """Получить queryset медицинских карточек в зависимости от роли пользователя."""
    if user.role == 'superadmin':
        return MedicalRecord.objects.all()
    elif user.role == 'hospital_admin':
        return MedicalRecord.objects.filter(patient__hospital=user.hospital)
    else:  # doctor
        return MedicalRecord.objects.filter(doctor=user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cabinet_view(request):
    """Кабинет врача - статистика и последние записи."""
    user = request.user
    
    patients_queryset = get_patient_queryset(user)
    records_queryset = get_medical_record_queryset(user)
    
    # Статистика
    total_patients = patients_queryset.count()
    total_records = records_queryset.count()
    
    # Последние 5 пациентов
    recent_patients = patients_queryset[:5]
    recent_patients_data = PatientSerializer(recent_patients, many=True).data
    
    # Последние 5 карточек
    recent_records = records_queryset[:5]
    recent_records_data = MedicalRecordSerializer(recent_records, many=True).data
    
    return Response({
        'statistics': {
            'total_patients': total_patients,
            'total_records': total_records,
        },
        'recent_patients': recent_patients_data,
        'recent_records': recent_records_data,
    })


class PatientListCreateView(generics.ListCreateAPIView):
    """API endpoint for listing and creating patients."""
    
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = get_patient_queryset(user)
        
        # Поиск
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(middle_name__icontains=search) |
                Q(phone__icontains=search) |
                Q(email__icontains=search)
            )
        
        # Сортировка
        ordering = self.request.query_params.get('ordering', None)
        if ordering:
            queryset = queryset.order_by(ordering)
        
        return queryset
    
    def perform_create(self, serializer):
        patient = serializer.save()
        # Автоматически создаем связь врач-пациент
        PatientDoctorRelation.objects.get_or_create(
            patient=patient,
            doctor=self.request.user,
            defaults={'is_active': True}
        )


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for patient detail, update and delete."""
    
    serializer_class = PatientWithRecordsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return get_patient_queryset(self.request.user)


class MedicalRecordListCreateView(generics.ListCreateAPIView):
    """API endpoint for listing and creating medical records."""
    
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = get_medical_record_queryset(user)
        
        # Фильтр по пациенту
        patient_id = self.request.query_params.get('patient', None)
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        # Сортировка
        ordering = self.request.query_params.get('ordering', '-visit_date')
        if ordering:
            queryset = queryset.order_by(ordering)
        
        return queryset
    
    def perform_create(self, serializer):
        # Автоматически устанавливаем врача
        serializer.save(doctor=self.request.user)


class MedicalRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for medical record detail, update and delete."""
    
    serializer_class = MedicalRecordDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return get_medical_record_queryset(self.request.user)
