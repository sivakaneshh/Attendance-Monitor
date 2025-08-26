# attendance/utils.py
from .models import Attendance, Holiday, Student
from datetime import date

def mark_attendance(rfid_uid):
    today = date.today()

    # check if today is holiday
    if Holiday.objects.filter(date=today).exists():
        return "Today is a holiday"

    try:
        student = Student.objects.get(rfid_uid=rfid_uid)
    except Student.DoesNotExist:
        return "Unknown card"

    attendance, created = Attendance.objects.get_or_create(
        student=student, date=today,
        defaults={'status': 'Present'}
    )

    if not created:
        attendance.status = 'Absent' if attendance.status == 'Present' else 'Present'
        attendance.save()

    return f"{student} marked {attendance.status}"
