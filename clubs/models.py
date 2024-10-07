from datetime import timezone
import datetime
from django.db import models
from django.contrib.auth.models import User

class Club(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

class Problem(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    description = models.TextField()
    quote = models.FileField(upload_to='quotes/', blank=True, null=True)  # PDF uploads
    created_at = models.DateTimeField(null=True, blank=True)
    is_solved = models.BooleanField(default=False)  # Supervisor can see all clubs
    solved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f'{self.club.name} - {self.description[:50]}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True, blank=True)  # null if user sees all clubs
    is_supervisor = models.BooleanField(default=False)  # Supervisor can see all clubs

    def __str__(self):
        return self.user.username


