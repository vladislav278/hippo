from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import User
from .serializers import UserSerializer, UserRegistrationSerializer, LoginSerializer
from patients.models import Patient, MedicalRecord, PatientDoctorRelation


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


@login_required
def cabinet_view(request):
    """Личный кабинет врача - HTML страница."""
    user = request.user
    
    patients_queryset = get_patient_queryset(user)
    records_queryset = get_medical_record_queryset(user)
    
    # Статистика
    total_patients = patients_queryset.count()
    total_records = records_queryset.count()
    
    # Последние 5 пациентов
    recent_patients = list(patients_queryset[:5])
    
    # Последние 5 карточек
    recent_records = list(records_queryset.select_related('patient', 'doctor')[:5])
    
    context = {
        'user': user,
        'total_patients': total_patients,
        'total_records': total_records,
        'recent_patients': recent_patients,
        'recent_records': recent_records,
    }
    
    return render(request, 'accounts/cabinet.html', context)


# API Views
class RegisterView(generics.CreateAPIView):
    """API endpoint for user registration."""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create token for the new user
        token, created = Token.objects.get_or_create(user=user)
        
        # Return user data with token
        user_data = UserSerializer(user).data
        return Response({
            'user': user_data,
            'token': token.key,
            'message': 'Регистрация успешна.'
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """API endpoint for user login."""
    serializer = LoginSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    
    # Create or get token
    token, created = Token.objects.get_or_create(user=user)
    
    user_data = UserSerializer(user).data
    return Response({
        'user': user_data,
        'token': token.key,
        'message': 'Вход выполнен успешно.'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """API endpoint to get current authenticated user."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
