"""
Скрипт для установки пароля администратора при деплое
Выполняется автоматически при старте сервера
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User

def setup_admin():
    """Устанавливает пароль администратора если указан в переменных окружения"""
    admin_email = os.environ.get('ADMIN_EMAIL', '')
    admin_password = os.environ.get('ADMIN_PASSWORD', '')
    
    if not admin_email or not admin_password:
        print("ADMIN_EMAIL и ADMIN_PASSWORD не указаны, пропускаем установку пароля")
        return
    
    try:
        user = User.objects.get(email=admin_email)
        user.set_password(admin_password)
        user.save()
        print(f"Пароль администратора {admin_email} успешно обновлен")
    except User.DoesNotExist:
        print(f"Пользователь {admin_email} не найден. Создайте его через createsuperuser")
    except Exception as e:
        print(f"Ошибка при установке пароля: {e}")

if __name__ == '__main__':
    setup_admin()

