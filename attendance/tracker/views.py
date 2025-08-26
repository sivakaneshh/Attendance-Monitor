# attendance/views.py
from django.shortcuts import render, redirect
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from .models import Attendance, Student, Holiday
from datetime import date, timedelta
import json

def is_admin(user):
    """Check if user is admin or staff"""
    return user.is_staff or user.is_superuser

def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and (user.is_staff or user.is_superuser):
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')
            
    return render(request, 'login.html')

def logout_view(request):
    """Handle user logout"""
    logout(request)
    return redirect('login')

def attendance(request):
    """View function for marking attendance."""
    today = date.today()
    
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        try:
            # Try to find the student with the given ID
            student = Student.objects.get(rfid_uid=student_id)
            
            # Check if attendance already marked
            existing_record = Attendance.objects.filter(
                student=student,
                date=today
            ).first()
            
            if existing_record:
                messages.info(
                    request, 
                    f'Attendance already marked for {student.user.get_full_name()} today'
                )
            else:
                # Mark attendance
                Attendance.objects.create(
                    student=student,
                    date=today,
                    status='Present'
                )
                messages.success(
                    request, 
                    f'Attendance marked for {student.user.get_full_name()}'
                )
                
        except Student.DoesNotExist:
            messages.error(
                request, 
                'Invalid Student ID. Please try again or contact administrator.'
            )
    
    # Get today's attendance records
    records = (Attendance.objects
              .filter(date=today)
              .select_related('student', 'student__user')
              .order_by('-date'))
              
    return render(request, "attendance.html", {
        "records": records,
        "today": today
    })

@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def dashboard(request):
    """View function for displaying attendance statistics dashboard."""
    today = date.today()
    
    # Get total number of students
    total_students = Student.objects.count()
    
    # Get today's attendance statistics
    today_stats = Attendance.objects.filter(date=today).aggregate(
        present_count=Count('id', filter=Q(status='Present')),
        absent_count=Count('id', filter=Q(status='Absent'))
    )
    
    # Calculate attendance rate
    if total_students > 0:
        attendance_rate = (today_stats['present_count'] / total_students) * 100
    else:
        attendance_rate = 0
        
    # Get recent attendance records
    recent_records = (
        Attendance.objects
        .filter(date=today)
        .select_related('student')
        .order_by('-id')[:10]  # Last 10 entries
    )
    
    # Get weekly attendance data (for the chart)
    week_stats = []
    for i in range(7):
        day = today - timedelta(days=i)
        stats = Attendance.objects.filter(date=day).aggregate(
            present=Count('id', filter=Q(status='Present')),
            total=Count('id')
        )
        week_stats.append({
            'date': day.strftime('%A'),  # Day name
            'present': stats['present'],
            'total': stats['total']
        })
    week_stats.reverse()  # Show oldest to newest
    
    context = {
        'today': today,
        'total_students': total_students,
        'present_count': today_stats['present_count'],
        'absent_count': today_stats['absent_count'],
        'attendance_rate': round(attendance_rate, 1),
        'records': recent_records,
        'week_stats': json.dumps(week_stats),
    }
    
    return render(request, "dash.html", context)

@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def register_student(request):
    """View function for registering new students."""
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        rfid_uid = request.POST.get('rfid_uid')
        email = request.POST.get('email')

        # Check if ID number already exists
        if Student.objects.filter(rfid_uid=rfid_uid).exists():
            messages.error(request, 'This ID number is already registered.')
            return redirect('register_student')

        try:
            # Create User instance
            username = f"{first_name.lower()}.{last_name.lower()}"
            base_username = username
            counter = 1
            # Ensure unique username
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            user = User.objects.create(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email if email else ""
            )

            # Create Student instance
            Student.objects.create(
                user=user,
                rfid_uid=rfid_uid
            )

            messages.success(request, f'Successfully registered {first_name} {last_name}')
            return redirect('register_student')

        except Exception as e:
            messages.error(request, f'Error registering student: {str(e)}')
            return redirect('register_student')

    # Get all students for display
    students = Student.objects.select_related('user').order_by('-user__date_joined')
    return render(request, "registration.html", {"students": students})