from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()  # Obtiene el modelo de usuario que se está utilizando

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completada'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')  

    
    def save(self, *args, **kwargs):
        if self.status == 'completed' and self.completion_date is None:
            self.completion_date = timezone.now()
        super().save(*args, **kwargs)
    def __str__(self):
        return str(self.title)

