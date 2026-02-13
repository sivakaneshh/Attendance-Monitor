"""
Script to clear all attendance logs while keeping teams and students intact.
Useful for testing / resetting between days.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from tracker.models import AttendanceLog

if __name__ == '__main__':
    count = AttendanceLog.objects.count()
    AttendanceLog.objects.all().delete()
    print(f"Cleared {count} attendance log(s). Teams and students are untouched.")
