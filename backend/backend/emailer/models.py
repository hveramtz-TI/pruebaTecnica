from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils import timezone

class CustomUser(AbstractUser):
    """Usuario personalizado para el sorteo"""
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    is_email_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

class Contest(models.Model):
    """Modelo para el concurso/sorteo"""
    name = models.CharField(max_length=200, default="Sorteo San Valentín 2025")
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    winner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_contests')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Participant(models.Model):
    """Participantes del sorteo"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)
    is_eligible = models.BooleanField(default=False)  # Solo elegible si email está verificado
    
    class Meta:
        unique_together = ['user', 'contest']
    
    def __str__(self):
        return f"{self.user.email} - {self.contest.name}"

class EmailVerification(models.Model):
    """Tokens de verificación de email"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"Verification for {self.user.email}"