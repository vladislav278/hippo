from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with email as username and role-based access."""
    
    ROLE_CHOICES = [
        ('superadmin', 'Супер-администратор'),
        ('hospital_admin', 'Администратор больницы'),
        ('doctor', 'Врач'),
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
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
