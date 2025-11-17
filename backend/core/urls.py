"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include
from .views import home_view

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    
    # HTML views (cabinet)
    path('cabinet/', include('accounts.urls')),
    
    # API views
    path('api/accounts/', include('accounts.api_urls')),
    path('api/hospitals/', include('hospitals.urls')),
    path('api/patients/', include('patients.urls')),
]
