"""
Management command для генерации 5 начальных регистрационных ключей.
"""
from django.core.management.base import BaseCommand
from accounts.models import RegistrationKey


class Command(BaseCommand):
    help = 'Генерирует 5 начальных регистрационных ключей'

    def handle(self, *args, **options):
        count = 5
        created_keys = []
        
        for _ in range(count):
            key_obj = RegistrationKey.create_key(created_by=None)
            created_keys.append(key_obj.key)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Создано {count} регистрационных ключей:\n' + 
                '\n'.join([f'  - {key}' for key in created_keys])
            )
        )

