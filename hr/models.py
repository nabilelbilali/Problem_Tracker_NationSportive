from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
import logging

from django.core.exceptions import ValidationError
from datetime import datetime






class Club(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Employee(models.Model):
    ROLE_CHOICES = [
        ('cleaner', 'Cleaner'),
        ('security', 'Security'),
        ('commercial', 'Commercial'),
        ('sales_manager', 'Sales Manager'),
        ('coach', 'Coach'),
        ('head_coach', 'Head Coach'),
        ('manager', 'Manager'),
    ]
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    start_date = models.DateField()
    last_paid_month = models.DateField(null=True, blank=True)
    advance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)


    def __str__(self):
        return f"{self.full_name} - {self.role} ({self.club.name})"

class LiaisonOfficer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class AttendanceRecord(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    date = models.DateField(default=datetime.now())
    present = models.BooleanField(default=False)
    entrance_time = models.TimeField(null=True, blank=True)
    exit_time = models.TimeField(null=True, blank=True)
    exit_reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee.full_name} - {self.date} - {'Present' if self.present else 'Absent'}"

    class Meta:
        verbose_name = "Attendance Record"
        verbose_name_plural = "Attendance Records"


class DocumentRequest(models.Model):
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="document_requests")
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, null=True, blank=True)  # Link to club
    document_type = models.CharField(max_length=100)
    reason = models.TextField()
    status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )
    request_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.club:  # Automatically assign club from the user
            self.club = self.requested_by.userprofile.club
        super().save(*args, **kwargs)

    

    def __str__(self):
        return f"Request by {self.requested_by.username} for {self.employee.full_name}"
    

    def clean(self):
        if datetime.now().weekday() != 0:  # Monday is 0
            raise ValidationError("Requests can only be made on Mondays.")
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)   



    class Meta:
        permissions = [
            ('can_request_documents', 'Can request documents'),
            ('can_manage_requests', 'Can manage document requests'),
        ]








