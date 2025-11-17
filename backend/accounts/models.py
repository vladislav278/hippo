from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with email as username and role-based access."""
    
    ROLE_CHOICES = [
        ('superadmin', 'Супер-администратор'),
        ('hospital_admin', 'Администратор больницы'),
        ('doctor', 'Врач'),
    ]
    
    SPECIALTY_CHOICES = [
        ('Кардиолог', 'Кардиолог'),
        ('Невролог', 'Невролог'),
        ('Пульмонолог', 'Пульмонолог'),
        ('Анестезиолог-реаниматолог', 'Анестезиолог-реаниматолог'),
        ('Рентгенолог', 'Рентгенолог'),
        ('Гастроэнтеролог', 'Гастроэнтеролог'),
        ('Хирург', 'Хирург'),
        ('Нефролог', 'Нефролог'),
        ('Уролог', 'Уролог'),
        ('ЛОР', 'ЛОР'),
    ]
    
    email = models.EmailField(unique=True, verbose_name="Email")
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='doctor',
        verbose_name="Роль"
    )
    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name="Больница"
    )
    specialty = models.CharField(
        max_length=100,
        choices=SPECIALTY_CHOICES,
        null=True,
        blank=True,
        verbose_name="Специализация"
    )
    last_activity = models.DateTimeField(null=True, blank=True, verbose_name="Последняя активность")

    def get_presence_status(self):
        """Возвращает ('online'|'recent'|'offline', emoji)."""
        from django.utils import timezone
        if not self.last_activity:
            return ('offline', '⚫')
        delta = timezone.now() - self.last_activity
        if delta.total_seconds() <= 5 * 60:
            return ('online', '🔵')
        if delta.total_seconds() <= 60 * 60:
            return ('recent', '🟡')
        return ('offline', '⚫')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    def get_initials(self):
        """Получить инициалы для аватара."""
        if self.first_name and self.last_name:
            return (self.first_name[0] + self.last_name[0]).upper()
        elif self.email:
            return self.email[0].upper()
        return 'U'
    
    def get_full_name(self):
        """Получить полное имя пользователя (ФИО)."""
        parts = []
        if self.last_name:
            parts.append(self.last_name)
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name or self.first_name:
            return ' '.join(parts)
        # Если нет ФИО, возвращаем email
        return self.email or 'Пользователь'
