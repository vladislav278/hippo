from django.db import models


class Hospital(models.Model):
    """Represents a clinic or medical organization."""
    
    name = models.CharField(max_length=255, verbose_name="Название")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Город")
    address = models.TextField(blank=True, null=True, verbose_name="Адрес")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    
    class Meta:
        verbose_name = "Больница"
        verbose_name_plural = "Больницы"
        ordering = ['name']
    
    def __str__(self):
        return self.name
