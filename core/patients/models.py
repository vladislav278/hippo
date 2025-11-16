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
