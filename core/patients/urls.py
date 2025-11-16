from django.urls import path
from .views import (
    PatientListView,
    PatientDetailView,
    MedicalRecordListView,
    MedicalRecordDetailView,
    doctor_cabinet_view,
)

app_name = 'patients'

urlpatterns = [
    # Кабинет врача
    path('cabinet/', doctor_cabinet_view, name='cabinet'),
    
    # Пациенты
    path('patients/', PatientListView.as_view(), name='patient-list'),
    path('patients/<int:pk>/', PatientDetailView.as_view(), name='patient-detail'),
    
    # Медицинские карточки
    path('records/', MedicalRecordListView.as_view(), name='record-list'),
    path('records/<int:pk>/', MedicalRecordDetailView.as_view(), name='record-detail'),
]

