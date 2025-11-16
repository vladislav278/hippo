"""
Django management команда для просмотра всех пользователей
Использование: python manage.py show_users
"""
from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Показывает всех пользователей в базе данных'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("ПОЛЬЗОВАТЕЛИ В БАЗЕ ДАННЫХ"))
        self.stdout.write("=" * 60)

        users = User.objects.all()

        if users:
            for u in users:
                self.stdout.write(f"\nEmail: {u.email}")
                self.stdout.write(f"Username: {u.username}")
                self.stdout.write(f"Role: {u.role}")
                if u.hospital:
                    self.stdout.write(f"Hospital: {u.hospital.name}")
                else:
                    self.stdout.write(f"Hospital: Нет")
                self.stdout.write(f"Is Staff: {u.is_staff}")
                self.stdout.write(f"Is Superuser: {u.is_superuser}")
                self.stdout.write(f"Date Joined: {u.date_joined}")
                self.stdout.write("-" * 60)

            self.stdout.write(f"\nВсего пользователей: {users.count()}")

            superusers = users.filter(is_superuser=True)
            if superusers:
                self.stdout.write(self.style.WARNING(f"\nСуперпользователи (админы):"))
                for su in superusers:
                    self.stdout.write(self.style.SUCCESS(f"  - {su.email}"))
        else:
            self.stdout.write(self.style.ERROR("\nПользователей нет в базе данных"))
            self.stdout.write("\nСоздайте суперпользователя командой:")
            self.stdout.write(self.style.WARNING("  python manage.py createsuperuser"))

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.WARNING("ВАЖНО: Пароли хранятся в хешированном виде"))
        self.stdout.write("   Их нельзя просто посмотреть!")
        self.stdout.write("   Для сброса пароля используйте:")
        self.stdout.write(self.style.WARNING("   python manage.py changepassword <email>"))
        self.stdout.write("=" * 60)

