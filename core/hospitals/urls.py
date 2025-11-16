from django.urls import path
from .views import HospitalListView

app_name = 'hospitals'
# fwrca
urlpatterns = [
    path('', HospitalListView.as_view(), name='list'),
]

