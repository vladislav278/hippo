from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def home_view(request):
    """Главная страница с информацией об API."""
    api_info = {
        "project": "Третье мнение - Платформа для консилиумов врачей",
        "version": "1.0.0",
        "endpoints": {
            "accounts": {
                "register": {
                    "url": "/api/accounts/register/",
                    "method": "POST",
                    "description": "Регистрация нового пользователя",
                    "authentication": "not required"
                },
                "login": {
                    "url": "/api/accounts/login/",
                    "method": "POST",
                    "description": "Вход в систему",
                    "authentication": "not required"
                },
                "me": {
                    "url": "/api/accounts/me/",
                    "method": "GET",
                    "description": "Информация о текущем пользователе",
                    "authentication": "required"
                }
            },
            "hospitals": {
                "list": {
                    "url": "/api/hospitals/",
                    "method": "GET",
                    "description": "Список больниц",
                    "authentication": "not required"
                },
                "create": {
                    "url": "/api/hospitals/",
                    "method": "POST",
                    "description": "Создать больницу",
                    "authentication": "required"
                }
            },
            "patients": {
                "cabinet": {
                    "url": "/api/patients/cabinet/",
                    "method": "GET",
                    "description": "Кабинет врача со статистикой",
                    "authentication": "required"
                },
                "patient_list": {
                    "url": "/api/patients/patients/",
                    "method": "GET",
                    "description": "Список пациентов",
                    "authentication": "required"
                },
                "patient_create": {
                    "url": "/api/patients/patients/",
                    "method": "POST",
                    "description": "Создать пациента",
                    "authentication": "required"
                },
                "patient_detail": {
                    "url": "/api/patients/patients/<id>/",
                    "method": "GET, PUT, PATCH, DELETE",
                    "description": "Детальная информация о пациенте",
                    "authentication": "required"
                },
                "record_list": {
                    "url": "/api/patients/records/",
                    "method": "GET",
                    "description": "Список медицинских карточек",
                    "authentication": "required"
                },
                "record_create": {
                    "url": "/api/patients/records/",
                    "method": "POST",
                    "description": "Создать медицинскую карточку",
                    "authentication": "required"
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

