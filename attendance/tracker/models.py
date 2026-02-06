from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Team(models.Model):
    """
    Represents a team in the RFID attendance system.
    Max 25 teams, each with exactly 6 students.
    """
    team_name = models.CharField(max_length=100, unique=True)
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['team_name']

    def __str__(self):
        return f"{self.team_name} ({'Complete' if self.is_complete else 'Incomplete'})"

    def get_student_count(self):
        """Return the number of students in this team."""
        return self.students.count()

    def clean(self):
        """Validate team creation constraints."""
        # Check if we already have 25 teams
        if not self.pk and Team.objects.count() >= 25:
            raise ValidationError("Maximum of 25 teams allowed.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Student(models.Model):
    """
    Represents a student with RFID card.
    Each student belongs to exactly one team.
    """
    name = models.CharField(max_length=200)
    rfid_uid = models.CharField(max_length=100, unique=True, db_index=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='students')
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['team', 'name']

    def __str__(self):
        return f"{self.name} ({self.team.team_name}) - RFID: {self.rfid_uid}"

    def clean(self):
        """Validate student registration constraints."""
        # Check if RFID is already registered
        if self.rfid_uid:
            existing = Student.objects.filter(rfid_uid=self.rfid_uid).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError(f"RFID {self.rfid_uid} is already registered.")

        # Check if team already has 6 students
        if self.team:
            current_count = self.team.students.exclude(pk=self.pk).count()
            if current_count >= 6:
                raise ValidationError(f"Team {self.team.team_name} already has 6 students.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Auto-complete team when 6th student is added
        if self.team.students.count() == 6:
            self.team.is_complete = True
            self.team.save()


class AttendanceLog(models.Model):
    """
    Tracks check-in/check-out events for students via RFID taps.
    Alternates between IN and OUT status.
    """
    STATUS_CHOICES = [
        ('IN', 'Checked In'),
        ('OUT', 'Checked Out'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_logs')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='attendance_logs')
    status = models.CharField(max_length=3, choices=STATUS_CHOICES)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.name} - {self.status} at {self.created_at}"

    def save(self, *args, **kwargs):
        # Automatically set check_in_time or check_out_time based on status
        if self.status == 'IN' and not self.check_in_time:
            self.check_in_time = timezone.now()
        elif self.status == 'OUT' and not self.check_out_time:
            self.check_out_time = timezone.now()
        super().save(*args, **kwargs)
