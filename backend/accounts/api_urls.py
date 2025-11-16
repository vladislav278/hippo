from django.urls import path
from .views import RegisterView, login_view, current_user_view

app_name = 'accounts-api'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', login_view, name='login'),
    path('me/', current_user_view, name='me'),
]

