"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from .views import home_view

urlpatterns = [
    path('', lambda request: redirect('cabinet') if request.user.is_authenticated else redirect('admin:index'), name='home'),
    path('admin/', admin.site.urls),
    
    # HTML views (cabinet)
    path('cabinet/', include('accounts.urls')),
    
    # API views
    path('api/accounts/', include('accounts.api_urls')),
    path('api/hospitals/', include('hospitals.urls')),
    path('api/patients/', include('patients.urls')),
]
