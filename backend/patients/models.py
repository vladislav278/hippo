from django.db import models
from django.conf import settings


class Patient(models.Model):
    """Модель пациента."""
    
    GENDER_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
        ('O', 'Другое'),
    ]
    
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Отчество")
    date_of_birth = models.DateField(verbose_name="Дата рождения")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Пол")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    address = models.TextField(blank=True, null=True, verbose_name="Адрес")
    
    # Связь с больницей (опционально, если пациент привязан к конкретной больнице)
    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patients',
        verbose_name="Больница"
    )
    
    # Данные из ЕМИАС
    emias_last_synced = models.DateTimeField(blank=True, null=True, verbose_name="Последняя синхронизация с ЕМИАС")
    emias_lab_results = models.JSONField(default=dict, blank=True, verbose_name="Лабораторные результаты (ЕМИАС)")
    last_hospitalization = models.TextField(blank=True, null=True, verbose_name="Последняя госпитализация")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    
    class Meta:
        verbose_name = "Пациент"
        verbose_name_plural = "Пациенты"
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name or ''}".strip()
    
    @property
    def full_name(self):
        """Полное имя пациента."""
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(parts)
    
    @property
    def age(self):
        """Вычислить возраст пациента."""
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    @property
    def card_number(self):
        """Номер медицинской карты (используем ID)."""
        return f"{self.id:06d}"
    
    @property
    def main_diagnosis(self):
        """Основной диагноз из последнего активного консилиума или медицинской карты."""
        # Сначала проверяем активные консилиумы
        active_case = self.cases.filter(status__in=['urgent', 'monitoring']).order_by('-created_at').first()
        if active_case and active_case.diagnosis:
            # Берем первые слова диагноза (до запятой или скобки, максимум 3 слова)
            diagnosis = active_case.diagnosis.split(',')[0].split('(')[0].strip()
            words = diagnosis.split()[:3]
            return ' '.join(words) if words else None
        
        # Если нет активных консилиумов, берем из последнего консилиума
        last_case = self.cases.order_by('-created_at').first()
        if last_case and last_case.diagnosis:
            diagnosis = last_case.diagnosis.split(',')[0].split('(')[0].strip()
            words = diagnosis.split()[:3]
            return ' '.join(words) if words else None
        
        # Если нет консилиумов, берем из последней медицинской карты
        last_record = self.medical_records.order_by('-visit_date').first()
        if last_record and last_record.diagnosis:
            diagnosis = last_record.diagnosis.split(',')[0].split('(')[0].strip()
            words = diagnosis.split()[:3]
            return ' '.join(words) if words else None
        
        return None
    
    def has_active_consilium(self, doctor=None):
        """Проверить, есть ли у пациента активный консилиум."""
        qs = self.cases.filter(status__in=['urgent', 'monitoring'])
        if doctor:
            qs = qs.filter(doctors=doctor)
        return qs.exists()
    
    def get_gender_display_short(self):
        """Короткое отображение пола."""
        if self.gender == 'M':
            return 'Муж'
        elif self.gender == 'F':
            return 'Жен'
        return '—'
    
    def get_allergies_list(self):
        """Получить список аллергий из последней медицинской карты."""
        last_record = self.medical_records.order_by('-visit_date').first()
        if last_record and last_record.allergies:
            # Парсим аллергии (предполагаем формат: "Аллерген1 (комментарий1), Аллерген2 (комментарий2)")
            allergies = []
            for item in last_record.allergies.split(','):
                item = item.strip()
                if '(' in item and ')' in item:
                    allergen, comment = item.split('(', 1)
                    comment = comment.rstrip(')').strip()
                    allergies.append({'name': allergen.strip(), 'comment': comment})
                else:
                    allergies.append({'name': item, 'comment': ''})
            return allergies
        return []
    
    def get_last_lab_results(self):
        """Получить последние лабораторные результаты."""
        if self.emias_lab_results:
            return self.emias_lab_results
        return {}


class MedicalRecord(models.Model):
    """Медицинская карточка пациента."""
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='medical_records',
        verbose_name="Пациент"
    )
    
    # Врач, который создал/ведет эту карточку
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='medical_records',
        verbose_name="Врач"
    )
    
    # Основные медицинские данные
    chief_complaint = models.TextField(verbose_name="Жалобы", help_text="Основные жалобы пациента")
    diagnosis = models.CharField(max_length=500, blank=True, null=True, verbose_name="Диагноз")
    anamnesis = models.TextField(blank=True, null=True, verbose_name="Анамнез", help_text="История заболевания")
    allergies = models.TextField(blank=True, null=True, verbose_name="Аллергии")
    chronic_diseases = models.TextField(blank=True, null=True, verbose_name="Хронические заболевания")
    current_medications = models.TextField(blank=True, null=True, verbose_name="Текущие препараты")
    notes = models.TextField(blank=True, null=True, verbose_name="Примечания")
    
    # Дата визита/создания записи
    visit_date = models.DateField(verbose_name="Дата визита")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    
    class Meta:
        verbose_name = "Медицинская карточка"
        verbose_name_plural = "Медицинские карточки"
        ordering = ['-visit_date', '-created_at']
    
    def __str__(self):
        return f"Карточка {self.patient.full_name} от {self.visit_date}"


class PatientDoctorRelation(models.Model):
    """Связь между пациентом и врачом (кто лечит пациента)."""
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='treating_doctors',
        verbose_name="Пациент"
    )
    
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patients',
        verbose_name="Врач"
    )
    
    # Когда врач начал лечить этого пациента
    assigned_date = models.DateField(auto_now_add=True, verbose_name="Дата назначения")
    
    # Активна ли связь (пациент все еще лечится у этого врача)
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    
    notes = models.TextField(blank=True, null=True, verbose_name="Примечания")
    
    class Meta:
        verbose_name = "Связь врач-пациент"
        verbose_name_plural = "Связи врач-пациент"
        unique_together = ['patient', 'doctor']
        ordering = ['-assigned_date']
    
    def __str__(self):
        return f"{self.doctor.email} лечит {self.patient.full_name}"


class Case(models.Model):
    """Консилиум - обсуждение между врачами по конкретному пациенту."""
    
    STATUS_CHOICES = [
        ('urgent', 'Срочно'),
        ('monitoring', 'Наблюдение'),
        ('stable', 'Стабильный'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='cases',
        verbose_name="Пациент"
    )
    
    # Врач, который создал консилиум
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_cases',
        verbose_name="Создал"
    )
    
    # Врачи, участвующие в консилиуме
    doctors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='cases',
        verbose_name="Врачи"
    )
    
    # Диагноз (МКБ-10)
    diagnosis = models.CharField(max_length=500, verbose_name="Диагноз (МКБ-10)")
    
    # Статус консилиума
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='monitoring',
        verbose_name="Статус"
    )
    
    # Описание случая
    description = models.TextField(verbose_name="Описание случая")
    
    # Дата поступления/создания консилиума
    admission_date = models.DateField(verbose_name="Дата поступления")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    
    class Meta:
        verbose_name = "Консилиум"
        verbose_name_plural = "Консилиумы"
        ordering = ['-admission_date', '-created_at']
    
    def __str__(self):
        return f"Консилиум: {self.patient.full_name} - {self.diagnosis}"
    
    def get_unread_count(self, user):
        """Получить количество непрочитанных сообщений для пользователя."""
        return self.messages.filter(is_read=False).exclude(author=user).count()


class CaseMessage(models.Model):
    """Сообщение в консилиуме."""
    
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name="Консилиум"
    )
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='case_messages',
        verbose_name="Автор"
    )
    
    content = models.TextField(verbose_name="Содержание")
    
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    
    class Meta:
        verbose_name = "Сообщение консилиума"
        verbose_name_plural = "Сообщения консилиумов"
        ordering = ['created_at']
    
    def __str__(self):
        return f"Сообщение от {self.author.email} в консилиуме {self.case.id}"


class MessageReaction(models.Model):
    """Реакция на сообщение."""
    
    REACTION_CHOICES = [
        ('👍', '👍'),
        ('👎', '👎'),
    ]
    
    message = models.ForeignKey(
        CaseMessage,
        on_delete=models.CASCADE,
        related_name='reactions',
        verbose_name="Сообщение"
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='message_reactions',
        verbose_name="Пользователь"
    )
    
    reaction = models.CharField(
        max_length=2,
        choices=REACTION_CHOICES,
        verbose_name="Реакция"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    
    class Meta:
        verbose_name = "Реакция на сообщение"
        verbose_name_plural = "Реакции на сообщения"
        unique_together = ['message', 'user', 'reaction']
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.reaction} на сообщение {self.message.id}"
