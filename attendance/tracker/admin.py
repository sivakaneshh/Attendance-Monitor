# attendance/admin.py
from django.contrib import admin
from .models import Student, Attendance, Holiday

admin.site.register(Student)
admin.site.register(Attendance)
admin.site.register(Holiday)
