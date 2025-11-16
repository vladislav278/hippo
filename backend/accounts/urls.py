from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import cabinet_view

app_name = 'accounts'

urlpatterns = [
    path('', cabinet_view, name='cabinet'),
    path('logout/', LogoutView.as_view(), name='logout'),
]

