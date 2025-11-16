from django.urls import path
from .views import (
    cabinet_view,
    PatientListCreateView, PatientDetailView,
    MedicalRecordListCreateView, MedicalRecordDetailView
)

app_name = 'patients'

urlpatterns = [
    path('cabinet/', cabinet_view, name='cabinet'),
    path('patients/', PatientListCreateView.as_view(), name='patient-list-create'),
    path('patients/<int:pk>/', PatientDetailView.as_view(), name='patient-detail'),
    path('records/', MedicalRecordListCreateView.as_view(), name='record-list-create'),
    path('records/<int:pk>/', MedicalRecordDetailView.as_view(), name='record-detail'),
]

