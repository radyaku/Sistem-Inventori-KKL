from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model dengan role Admin/Staff"""
    
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('staff', 'Staff'),
    ]
    
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='staff',
        verbose_name='Role'
    )
    
    class Meta:
        verbose_name = 'Pengguna'
        verbose_name_plural = 'Pengguna'
    
    def is_admin(self):
        return self.role == 'admin'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
