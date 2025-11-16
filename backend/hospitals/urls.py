from django.urls import path
from .views import HospitalListCreateView

app_name = 'hospitals'

urlpatterns = [
    path('', HospitalListCreateView.as_view(), name='list-create'),
]

