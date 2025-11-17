from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from patients.models import Patient
from hospitals.models import Hospital


@require_http_methods(["GET"])
def home_view(request):
    """Главная страница."""
    context = {
        'is_authenticated': request.user.is_authenticated,
        'user': request.user,
    }
    
    # Статистика для неавторизованных пользователей
    if not request.user.is_authenticated:
        context.update({
            'total_hospitals': Hospital.objects.count(),
            'total_patients': Patient.objects.count(),
        })
    
    return render(request, 'core/home.html', context)

