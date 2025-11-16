from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def home_view(request):
    """Главная страница API с информацией о доступных endpoints."""
    
    api_info = {
        "project": "Третье мнение - Платформа для консилиумов врачей",
        "version": "1.0.0",
        "description": "REST API для управления пациентами, медицинскими карточками и консилиумами",
        "endpoints": {
            "authentication": {
                "register": {
                    "url": "/api/accounts/register/",
                    "method": "POST",
                    "description": "Регистрация нового пользователя",
                    "required_fields": ["email", "username", "password", "password_confirm"],
                    "optional_fields": ["role", "hospital"]
                },
                "login": {
                    "url": "/api/accounts/login/",
                    "method": "POST",
                    "description": "Вход в систему",
                    "required_fields": ["email", "password"]
                },
                "current_user": {
                    "url": "/api/accounts/me/",
                    "method": "GET",
                    "description": "Получить информацию о текущем пользователе",
                    "authentication": "required"
                }
            },
            "hospitals": {
                "list": {
                    "url": "/api/hospitals/",
                    "method": "GET",
                    "description": "Список всех больниц (публичный)"
                },
                "create": {
                    "url": "/api/hospitals/",
                    "method": "POST",
                    "description": "Создать новую больницу",
                    "authentication": "required"
                }
            },
            "patients": {
                "cabinet": {
                    "url": "/api/patients/cabinet/",
                    "method": "GET",
                    "description": "Кабинет врача - статистика и краткая информация",
                    "authentication": "required"
                },
                "patient_list": {
                    "url": "/api/patients/patients/",
                    "method": "GET, POST",
                    "description": "Список пациентов врача / Создать пациента",
                    "authentication": "required",
                    "search": "?search=query",
                    "ordering": "?ordering=last_name"
                },
                "patient_detail": {
                    "url": "/api/patients/patients/<id>/",
                    "method": "GET, PUT, PATCH, DELETE",
                    "description": "Детальная информация о пациенте",
                    "authentication": "required"
                },
                "records_list": {
                    "url": "/api/patients/records/",
                    "method": "GET, POST",
                    "description": "Список медицинских карточек / Создать карточку",
                    "authentication": "required",
                    "filter": "?patient=<id>"
                },
                "record_detail": {
                    "url": "/api/patients/records/<id>/",
                    "method": "GET, PUT, PATCH, DELETE",
                    "description": "Детальная информация о медицинской карточке",
                    "authentication": "required"
                }
            },
            "admin": {
                "url": "/admin/",
                "description": "Django Admin панель для управления данными"
            }
        },
        "authentication": {
            "type": "Token Authentication",
            "header": "Authorization: Token <your_token>",
            "how_to_get_token": "Зарегистрируйтесь или войдите через /api/accounts/register/ или /api/accounts/login/"
        },
        "documentation": {
            "browsable_api": "Все endpoints доступны через DRF Browsable API - просто откройте любой URL в браузере",
            "examples": {
                "register": "POST /api/accounts/register/ с телом: {\"email\": \"doctor@example.com\", \"username\": \"doctor1\", \"password\": \"pass123\", \"password_confirm\": \"pass123\"}",
                "login": "POST /api/accounts/login/ с телом: {\"email\": \"doctor@example.com\", \"password\": \"pass123\"}",
                "cabinet": "GET /api/patients/cabinet/ с заголовком: Authorization: Token <your_token>"
            }
        }
    }
    
    return JsonResponse(api_info, json_dumps_params={'ensure_ascii': False, 'indent': 2})

