from django.contrib.auth.models import AbstractUser
from django.db import models
import secrets
import string


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
    patronymic = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name="Отчество"
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
        if self.patronymic:
            parts.append(self.patronymic)
        if parts:
            return ' '.join(parts)
        # Если нет ФИО, возвращаем email
        return self.email or 'Пользователь'


class RegistrationKey(models.Model):
    """Одноразовый ключ для регистрации врачей."""
    
    key = models.CharField(max_length=32, unique=True, verbose_name="Ключ")
    is_used = models.BooleanField(default=False, verbose_name="Использован")
    used_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registration_keys',
        verbose_name="Использован пользователем"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_registration_keys',
        verbose_name="Создан пользователем"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    used_at = models.DateTimeField(null=True, blank=True, verbose_name="Использован")
    
    class Meta:
        verbose_name = "Регистрационный ключ"
        verbose_name_plural = "Регистрационные ключи"
        ordering = ['-created_at']
    
    def __str__(self):
        status = "Использован" if self.is_used else "Активен"
        return f"{self.key} ({status})"
    
    @staticmethod
    def generate_key(length=16):
        """Генерирует случайный ключ."""
        alphabet = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @classmethod
    def create_key(cls, created_by=None):
        """Создает новый регистрационный ключ."""
        key = cls.generate_key()
        # Убеждаемся, что ключ уникален
        while cls.objects.filter(key=key).exists():
            key = cls.generate_key()
        return cls.objects.create(key=key, created_by=created_by)
    
    def use(self, user):
        """Помечает ключ как использованный."""
        from django.utils import timezone
        self.is_used = True
        self.used_by = user
        self.used_at = timezone.now()
        self.save()
