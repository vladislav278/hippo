"""
Скрипт для автоматической настройки админа на Railway.
Используется в Procfile после миграций.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User

def setup_admin():
    """Создает или обновляет админа из переменных окружения."""
    admin_email = os.environ.get('ADMIN_EMAIL')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    admin_first_name = os.environ.get('ADMIN_FIRST_NAME', 'Admin')
    admin_last_name = os.environ.get('ADMIN_LAST_NAME', 'User')
    
    if admin_email and admin_password:
        admin, created = User.objects.get_or_create(
            email=admin_email,
            defaults={
                'first_name': admin_first_name,
                'last_name': admin_last_name,
                'role': 'superadmin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        if not created:
            # Обновляем существующего админа
            admin.first_name = admin_first_name
            admin.last_name = admin_last_name
            admin.role = 'superadmin'
            admin.is_staff = True
            admin.is_superuser = True
        
        admin.set_password(admin_password)
        admin.save()
        
        if created:
            print(f'✅ Админ создан: {admin_email}')
        else:
            print(f'✅ Админ обновлен: {admin_email}')
    else:
        print('⚠️  ADMIN_EMAIL и ADMIN_PASSWORD не установлены. Пропускаем создание админа.')

if __name__ == '__main__':
    setup_admin()

