# attendance/views.py
from django.shortcuts import render
from .models import Attendance, Student, Holiday
from datetime import date

def dashboard(request):
    today = date.today()
    records = Attendance.objects.filter(date=today).select_related("student")
    return render(request, "dash.html", {"records": records, "today": today})
    