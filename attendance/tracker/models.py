from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rfid_uid = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Holiday(models.Model):
    date = models.DateField(unique=True)
    description = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.date} - {self.description}"

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Holiday', 'Holiday'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Absent')

    class Meta:
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"
