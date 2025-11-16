"""
Django management команда для установки пароля администратора
Использование: python manage.py set_admin_password <email> <password>
"""
from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Устанавливает пароль для администратора по email'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email администратора')
        parser.add_argument('password', type=str, help='Новый пароль')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        
        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Пароль успешно изменен для пользователя {email}')
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Пользователь с email {email} не найден')
            )

