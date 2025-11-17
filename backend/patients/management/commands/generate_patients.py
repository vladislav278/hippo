from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random
from patients.models import Patient
from hospitals.models import Hospital


class Command(BaseCommand):
    help = 'Генерирует тестовых пациентов'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Количество пациентов для генерации (по умолчанию: 10)',
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Русские имена и фамилии
        first_names_male = [
            'Александр', 'Дмитрий', 'Максим', 'Сергей', 'Андрей',
            'Алексей', 'Артем', 'Илья', 'Кирилл', 'Михаил',
            'Никита', 'Матвей', 'Роман', 'Егор', 'Арсений'
        ]
        
        first_names_female = [
            'Анна', 'Мария', 'Елена', 'Наталья', 'Ольга',
            'Татьяна', 'Ирина', 'Екатерина', 'Светлана', 'Юлия',
            'Анастасия', 'Дарья', 'Евгения', 'Валентина', 'Галина'
        ]
        
        last_names = [
            'Иванов', 'Петров', 'Сидоров', 'Смирнов', 'Кузнецов',
            'Попов', 'Соколов', 'Лебедев', 'Козлов', 'Новиков',
            'Морозов', 'Петухов', 'Волков', 'Соловьев', 'Васильев',
            'Зайцев', 'Павлов', 'Семенов', 'Голубев', 'Виноградов'
        ]
        
        middle_names_male = [
            'Александрович', 'Дмитриевич', 'Максимович', 'Сергеевич', 'Андреевич',
            'Алексеевич', 'Артемович', 'Ильич', 'Кириллович', 'Михайлович'
        ]
        
        middle_names_female = [
            'Александровна', 'Дмитриевна', 'Максимовна', 'Сергеевна', 'Андреевна',
            'Алексеевна', 'Артемовна', 'Ильинична', 'Кирилловна', 'Михайловна'
        ]
        
        cities = ['Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань']
        streets = ['Ленина', 'Пушкина', 'Гагарина', 'Мира', 'Советская', 'Центральная']
        
        # Получаем все больницы (если есть)
        hospitals = list(Hospital.objects.all())
        
        created_count = 0
        
        for i in range(count):
            # Случайный пол
            gender = random.choice(['M', 'F'])
            
            if gender == 'M':
                first_name = random.choice(first_names_male)
                middle_name = random.choice(middle_names_male)
            else:
                first_name = random.choice(first_names_female)
                middle_name = random.choice(middle_names_female)
            
            last_name = random.choice(last_names)
            
            # Дата рождения (от 18 до 80 лет назад)
            years_ago = random.randint(18, 80)
            birth_date = date.today() - timedelta(days=years_ago * 365 + random.randint(0, 365))
            
            # Телефон
            phone = f"+7{random.randint(900, 999)}{random.randint(1000000, 9999999)}"
            
            # Email
            email = f"{first_name.lower()}.{last_name.lower()}{i}@example.com"
            
            # Адрес
            address = f"г. {random.choice(cities)}, ул. {random.choice(streets)}, д. {random.randint(1, 100)}, кв. {random.randint(1, 200)}"
            
            # Больница (опционально)
            hospital = random.choice(hospitals) if hospitals else None
            
            patient = Patient.objects.create(
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                date_of_birth=birth_date,
                gender=gender,
                phone=phone,
                email=email,
                address=address,
                hospital=hospital
            )
            
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'{created_count}. Создан пациент: {patient.full_name} ({patient.get_gender_display()}, {patient.date_of_birth})'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nУспешно создано {created_count} пациентов!')
        )

