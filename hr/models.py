from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
import logging







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








