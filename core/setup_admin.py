"""
Скрипт для установки пароля администратора при деплое
Выполняется автоматически при старте сервера
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

try:
    django.setup()
except Exception as e:
    print(f"Ошибка при настройке Django: {e}", file=sys.stderr)
    sys.exit(1)

from accounts.models import User  # noqa


def setup_admin():
    """Устанавливает пароль администратора если указан в переменных окружения"""
    print("=" * 60)
    print("Запуск setup_admin.py")
    print("=" * 60)
    
    admin_email = os.environ.get('ADMIN_EMAIL', '')
    admin_password = os.environ.get('ADMIN_PASSWORD', '')
    
    print(f"ADMIN_EMAIL: {'указан' if admin_email else 'НЕ указан'}")
    print(f"ADMIN_PASSWORD: {'указан' if admin_password else 'НЕ указан'}")
    
    if not admin_email or not admin_password:
        print("⚠️  ADMIN_EMAIL и ADMIN_PASSWORD не указаны → пропускаем установку пароля")
        print("   Добавьте переменные окружения на Railway для автоматической установки")
        return
    
    try:
        user, created = User.objects.get_or_create(
            email=admin_email,
            defaults={
                "username": admin_email.split('@')[0],  # Используем часть до @ как username
                "is_superuser": True,
                "is_staff": True,
                "role": "superadmin",
            },
        )
        
        user.set_password(admin_password)
        user.is_superuser = True
        user.is_staff = True
        user.role = "superadmin"
        user.save()
        
        if created:
            print(f"✅ Создан суперпользователь: {admin_email}")
        else:
            print(f"✅ Обновлён пароль суперпользователя: {admin_email}")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Ошибка при установке пароля: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    setup_admin()


