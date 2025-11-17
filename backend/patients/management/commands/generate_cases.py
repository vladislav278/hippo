from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random
from patients.models import Patient, Case, CaseMessage
from accounts.models import User


class Command(BaseCommand):
    help = 'Генерирует тестовые консилиумы'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Количество консилиумов для генерации (по умолчанию: 10)',
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Диагнозы (МКБ-10)
        diagnoses = [
            'I10 Эссенциальная (первичная) гипертензия',
            'E11 Сахарный диабет 2 типа',
            'J44 Другая хроническая обструктивная легочная болезнь',
            'I25 Хроническая ишемическая болезнь сердца',
            'K59.0 Запор',
            'M79.3 Панникулит неуточненный',
            'G93.4 Энцефалопатия неуточненная',
            'N18 Хроническая болезнь почек',
            'I50 Сердечная недостаточность',
            'J18 Пневмония неуточненного возбудителя',
        ]
        
        # Описания случаев
        descriptions = [
            'Пациент поступил с жалобами на головную боль и повышение артериального давления.',
            'Требуется консультация по поводу коррекции терапии.',
            'Сложный случай, требующий мнения нескольких специалистов.',
            'Необходимо обсуждение тактики лечения.',
            'Пациент с множественными сопутствующими заболеваниями.',
        ]
        
        # Получаем пациентов и врачей
        patients = list(Patient.objects.all())
        doctors = list(User.objects.filter(role='doctor'))
        
        if not patients:
            self.stdout.write(self.style.ERROR('Нет пациентов в базе. Сначала создайте пациентов.'))
            return
        
        if not doctors:
            self.stdout.write(self.style.ERROR('Нет врачей в базе. Сначала создайте врачей.'))
            return
        
        created_count = 0
        
        for i in range(count):
            # Случайный пациент
            patient = random.choice(patients)
            
            # Случайные врачи (от 2 до 4)
            num_doctors = random.randint(2, min(4, len(doctors)))
            case_doctors = random.sample(doctors, num_doctors)
            
            # Случайный диагноз
            diagnosis = random.choice(diagnoses)
            
            # Случайное описание
            description = random.choice(descriptions)
            
            # Статус - для базы знаний используем 'stable' (завершенные)
            status = 'stable'
            
            # Дата поступления (от 30 дней назад до сегодня)
            days_ago = random.randint(0, 30)
            admission_date = date.today() - timedelta(days=days_ago)
            
            # Создаем консилиум
            case = Case.objects.create(
                patient=patient,
                created_by=case_doctors[0],
                diagnosis=diagnosis,
                description=description,
                status=status,
                admission_date=admission_date
            )
            
            # Добавляем врачей
            case.doctors.set(case_doctors)
            
            # Создаем несколько сообщений
            num_messages = random.randint(1, 5)
            for j in range(num_messages):
                author = random.choice(case_doctors)
                content = f'Сообщение {j+1} от врача {author.email} по поводу пациента {patient.full_name}.'
                CaseMessage.objects.create(
                    case=case,
                    author=author,
                    content=content,
                    is_read=random.choice([True, False])
                )
            
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'{created_count}. Создан консилиум: {patient.full_name} - {diagnosis} ({case.get_status_display()})'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nУспешно создано {created_count} консилиумов!')
        )

