# tracker/views.py
"""
Views for RFID Team-Based Event Attendance System

This module provides:
1. HTML Interface Views - For browser-based management
2. RESTful API endpoints - For RFID hardware integration
"""
import csv as csv_module
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.db.models import Count, Q, Subquery, OuterRef, Exists
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import Team, Student, AttendanceLog
from .utils import RegistrationService, AttendanceService, TeamValidator


# ============================================================================
# HTML INTERFACE VIEWS
# ============================================================================

def login_view(request):
    """Render login page and handle authentication."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')


def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    """Render dashboard with attendance statistics."""
    today = timezone.now().date()
    
    # Get statistics
    total_students = Student.objects.count()
    
    # Get today's attendance - count unique students marked IN
    present_logs = AttendanceLog.objects.filter(
        check_in_time__date=today,
        status='IN'
    ).values('student').distinct()
    present_count = present_logs.count()
    
    absent_count = total_students - present_count
    attendance_rate = round((present_count / total_students * 100) if total_students > 0 else 0, 1)
    
    # Get recent attendance records (last 10)
    recent_records = AttendanceLog.objects.select_related(
        'student', 'student__team'
    ).order_by('-created_at')[:10]

    # --- Team-wise attendance breakdown ---
    # IDs of students who checked in today
    present_student_ids = set(
        AttendanceLog.objects.filter(
            created_at__date=today, status='IN'
        ).values_list('student_id', flat=True)
    )

    teams = Team.objects.prefetch_related('students').order_by('team_name')
    team_stats = []
    for team in teams:
        students = list(team.students.all())
        total = len(students)
        present = [s for s in students if s.id in present_student_ids]
        absent = [s for s in students if s.id not in present_student_ids]
        team_stats.append({
            'team': team,
            'total': total,
            'present_count': len(present),
            'absent_count': len(absent),
            'present_students': present,
            'absent_students': absent,
            'rate': round(len(present) / total * 100, 1) if total > 0 else 0,
        })
    
    context = {
        'today': today,
        'total_students': total_students,
        'present_count': present_count,
        'absent_count': absent_count,
        'attendance_rate': attendance_rate,
        'records': recent_records,
        'team_stats': team_stats,
        'total_teams': teams.count(),
    }
    
    return render(request, 'dash.html', context)


@login_required(login_url='login')
def download_attendance_csv(request):
    """Download today's attendance summary as CSV."""
    today = timezone.now().date()

    present_student_ids = set(
        AttendanceLog.objects.filter(
            created_at__date=today, status='IN'
        ).values_list('student_id', flat=True)
    )

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_{today}.csv"'

    writer = csv_module.writer(response)
    writer.writerow(['Team', 'Student Name', 'RFID', 'Status', 'Last Action Time'])

    teams = Team.objects.prefetch_related('students').order_by('team_name')
    for team in teams:
        for student in team.students.all().order_by('name'):
            is_present = student.id in present_student_ids
            last_log = AttendanceLog.objects.filter(
                student=student, created_at__date=today
            ).order_by('-created_at').first()
            last_time = last_log.created_at.strftime('%H:%M:%S') if last_log else '-'
            writer.writerow([
                team.team_name,
                student.name,
                student.rfid_uid,
                'Present' if is_present else 'Absent',
                last_time,
            ])

    return response


@login_required(login_url='login')
def registration_page(request):
    """Render student registration page and handle registration."""
    if request.method == 'POST':
        try:
            team_id = request.POST.get('team_id')
            student_name = request.POST.get('student_name', '').strip()
            rfid_uid = request.POST.get('rfid_uid', '').strip()
            
            if not all([team_id, student_name, rfid_uid]):
                messages.error(request, 'All fields are required')
            else:
                # Register student using service
                student = RegistrationService.register_student(team_id, student_name, rfid_uid)
                messages.success(request, f'Student {student_name} registered successfully!')
                return redirect('register_student')
                
        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    # Get all teams for the dropdown
    teams = Team.objects.annotate(
        student_count=Count('students')
    ).order_by('team_name')
    
    # Get all registered students
    students = Student.objects.select_related('team').order_by('-registered_at')
    
    context = {
        'teams': teams,
        'students': students,
    }
    
    return render(request, 'registration.html', context)


@login_required(login_url='login')
def team_management_page(request):
    """Render team management page and handle team creation."""
    if request.method == 'POST':
        try:
            team_name = request.POST.get('team_name', '').strip()
            
            if not team_name:
                messages.error(request, 'Team name is required')
            else:
                # Create team using service
                team = RegistrationService.create_team(team_name)
                messages.success(request, f'Team "{team_name}" created successfully!')
                return redirect('teams')
                
        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    # Get all teams
    teams = Team.objects.annotate(
        student_count=Count('students')
    ).order_by('team_name')
    
    context = {
        'teams': teams,
    }
    
    return render(request, 'teams.html', context)


@login_required(login_url='login')
def attendance_page(request):
    """Render attendance marking page and handle RFID taps."""
    if request.method == 'POST':
        try:
            rfid_uid = request.POST.get('student_id', '').strip()
            
            if not rfid_uid:
                messages.error(request, 'RFID UID is required')
            else:
                # Process tap using service
                result = AttendanceService.process_rfid_tap(rfid_uid)
                
                student_name = result['student_name']
                status = result['status']
                
                if status == 'IN':
                    messages.success(request, f'✓ {student_name} checked IN successfully')
                else:
                    messages.success(request, f'✓ {student_name} checked OUT successfully')
                    
                return redirect('attendance')
                
        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    # Get today's attendance records
    today = timezone.now().date()
    records = AttendanceLog.objects.filter(
        created_at__date=today
    ).select_related('student', 'student__team').order_by('-created_at')
    
    # Get live count of IN vs OUT
    live_count = AttendanceService.get_live_count()
    
    context = {
        'today': timezone.now(),
        'records': records,
        'in_count': live_count['in_count'],
        'out_count': live_count['out_count'],
        'total_students': live_count['total_students'],
    }
    
    return render(request, 'attendance.html', context)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def json_error_response(message, status=400):
    """Return a JSON error response."""
    return JsonResponse({'error': message}, status=status)


def json_success_response(data, status=200):
    """Return a JSON success response."""
    return JsonResponse(data, status=status)


def parse_json_body(request):
    """Parse JSON body from request."""
    try:
        return json.loads(request.body)
    except json.JSONDecodeError:
        raise ValidationError("Invalid JSON in request body")


# ============================================================================
# PHASE 1: TEAM REGISTRATION APIs
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def create_team(request):
    """
    Create a new team.
    
    POST /api/teams
    Body: { "team_name": "Team Alpha" }
    
    Returns:
        201: Team created successfully
        400: Validation error (duplicate name, limit reached, etc.)
    """
    try:
        data = parse_json_body(request)
        team_name = data.get('team_name', '').strip()
        
        if not team_name:
            return json_error_response("team_name is required")
        
        # Create team using service
        team = RegistrationService.create_team(team_name)
        
        return json_success_response({
            'id': team.id,
            'team_name': team.team_name,
            'is_complete': team.is_complete,
            'student_count': team.get_student_count(),
            'created_at': team.created_at.isoformat()
        }, status=201)
        
    except ValidationError as e:
        return json_error_response(str(e))
    except Exception as e:
        return json_error_response(f"Server error: {str(e)}", status=500)


@csrf_exempt
@require_http_methods(["POST"])
def register_student(request):
    """
    Register a student to a team with RFID.
    
    POST /api/students/register
    Body: {
        "team_id": 1,
        "student_name": "John Doe",
        "rfid_uid": "ABC123XYZ"
    }
    
    Returns:
        201: Student registered successfully
        400: Validation error (duplicate RFID, team full, etc.)
        404: Team not found
    """
    try:
        data = parse_json_body(request)
        
        team_id = data.get('team_id')
        student_name = data.get('student_name', '').strip()
        rfid_uid = data.get('rfid_uid', '').strip()
        
        # Validate required fields
        if not team_id:
            return json_error_response("team_id is required")
        if not student_name:
            return json_error_response("student_name is required")
        if not rfid_uid:
            return json_error_response("rfid_uid is required")
        
        # Register student using service
        student = RegistrationService.register_student(team_id, student_name, rfid_uid)
        
        # Get updated team info
        team = student.team
        
        return json_success_response({
            'id': student.id,
            'name': student.name,
            'rfid_uid': student.rfid_uid,
            'team': {
                'id': team.id,
                'team_name': team.team_name,
                'is_complete': team.is_complete,
                'student_count': team.get_student_count()
            },
            'registered_at': student.registered_at.isoformat()
        }, status=201)
        
    except ValidationError as e:
        return json_error_response(str(e))
    except Exception as e:
        return json_error_response(f"Server error: {str(e)}", status=500)


# ============================================================================
# PHASE 2: ATTENDANCE TRACKING APIs
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def rfid_tap(request):
    """
    Process RFID tap for attendance (check-in/check-out toggle).
    
    POST /api/attendance/tap
    Body: { "rfid_uid": "ABC123XYZ" }
    
    Logic:
    - 1st tap: IN
    - 2nd tap: OUT
    - 3rd tap: IN
    - 4th tap: OUT
    ... continues toggling
    
    Returns:
        200: Attendance logged successfully
        400: RFID not registered
    """
    try:
        data = parse_json_body(request)
        rfid_uid = data.get('rfid_uid', '').strip()
        
        if not rfid_uid:
            return json_error_response("rfid_uid is required")
        
        # Process tap using service
        result = AttendanceService.process_rfid_tap(rfid_uid)
        
        return json_success_response({
            'message': f"Attendance logged: {result['status']}",
            'attendance_log': result
        }, status=200)
        
    except ValidationError as e:
        return json_error_response(str(e))
    except Exception as e:
        return json_error_response(f"Server error: {str(e)}", status=500)


# ============================================================================
# ADMIN QUERY APIs
# ============================================================================

@require_http_methods(["GET"])
def list_teams(request):
    """
    Get list of all teams.
    
    GET /api/teams
    
    Returns:
        200: List of all teams with student counts
    """
    try:
        teams = Team.objects.annotate(
            student_count=Count('students')
        ).order_by('team_name')
        
        teams_data = [{
            'id': team.id,
            'team_name': team.team_name,
            'is_complete': team.is_complete,
            'student_count': team.student_count,
            'created_at': team.created_at.isoformat()
        } for team in teams]
        
        return json_success_response({
            'total_teams': teams.count(),
            'teams': teams_data
        })
        
    except Exception as e:
        return json_error_response(f"Server error: {str(e)}", status=500)


@require_http_methods(["GET"])
def get_team_detail(request, team_id):
    """
    Get detailed information about a specific team.
    
    GET /api/teams/<team_id>
    
    Returns:
        200: Team details with all students
        404: Team not found
    """
    try:
        team = Team.objects.prefetch_related('students').get(id=team_id)
        
        students_data = [{
            'id': student.id,
            'name': student.name,
            'rfid_uid': student.rfid_uid,
            'registered_at': student.registered_at.isoformat()
        } for student in team.students.all()]
        
        return json_success_response({
            'id': team.id,
            'team_name': team.team_name,
            'is_complete': team.is_complete,
            'student_count': len(students_data),
            'created_at': team.created_at.isoformat(),
            'students': students_data
        })
        
    except Team.DoesNotExist:
        return json_error_response(f"Team with ID {team_id} not found", status=404)
    except Exception as e:
        return json_error_response(f"Server error: {str(e)}", status=500)


@require_http_methods(["GET"])
def get_team_attendance(request, team_id):
    """
    Get attendance history for a specific team.
    
    GET /api/attendance/team/<team_id>
    
    Returns:
        200: List of all attendance logs for the team
        404: Team not found
    """
    try:
        # Check if team exists
        team = Team.objects.get(id=team_id)
        
        # Get attendance logs
        logs = AttendanceService.get_team_attendance_history(team_id)
        
        logs_data = [{
            'id': log.id,
            'student': {
                'id': log.student.id,
                'name': log.student.name,
                'rfid_uid': log.student.rfid_uid
            },
            'status': log.status,
            'check_in_time': log.check_in_time.isoformat() if log.check_in_time else None,
            'check_out_time': log.check_out_time.isoformat() if log.check_out_time else None,
            'created_at': log.created_at.isoformat()
        } for log in logs]
        
        return json_success_response({
            'team_id': team.id,
            'team_name': team.team_name,
            'total_logs': len(logs_data),
            'attendance_logs': logs_data
        })
        
    except Team.DoesNotExist:
        return json_error_response(f"Team with ID {team_id} not found", status=404)
    except Exception as e:
        return json_error_response(f"Server error: {str(e)}", status=500)


@require_http_methods(["GET"])
def get_student_attendance(request, student_id):
    """
    Get attendance history for a specific student.
    
    GET /api/attendance/student/<student_id>
    
    Returns:
        200: List of all attendance logs for the student
        404: Student not found
    """
    try:
        # Check if student exists
        student = Student.objects.select_related('team').get(id=student_id)
        
        # Get attendance logs
        logs = AttendanceService.get_student_attendance_history(student_id)
        
        logs_data = [{
            'id': log.id,
            'status': log.status,
            'check_in_time': log.check_in_time.isoformat() if log.check_in_time else None,
            'check_out_time': log.check_out_time.isoformat() if log.check_out_time else None,
            'created_at': log.created_at.isoformat()
        } for log in logs]
        
        return json_success_response({
            'student': {
                'id': student.id,
                'name': student.name,
                'rfid_uid': student.rfid_uid,
                'team': {
                    'id': student.team.id,
                    'team_name': student.team.team_name
                }
            },
            'total_logs': len(logs_data),
            'attendance_logs': logs_data
        })
        
    except Student.DoesNotExist:
        return json_error_response(f"Student with ID {student_id} not found", status=404)
    except Exception as e:
        return json_error_response(f"Server error: {str(e)}", status=500)


# ============================================================================
# SYSTEM STATUS / HEALTH CHECK
# ============================================================================

@require_http_methods(["GET"])
def system_status(request):
    """
    Get system status and statistics.
    
    GET /api/status
    
    Returns:
        200: System statistics
    """
    try:
        total_teams = Team.objects.count()
        complete_teams = Team.objects.filter(is_complete=True).count()
        total_students = Student.objects.count()
        total_attendance_logs = AttendanceLog.objects.count()
        
        return json_success_response({
            'status': 'operational',
            'statistics': {
                'total_teams': total_teams,
                'complete_teams': complete_teams,
                'incomplete_teams': total_teams - complete_teams,
                'total_students': total_students,
                'total_attendance_logs': total_attendance_logs,
                'students_per_team': 6
            },
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        return json_error_response(f"Server error: {str(e)}", status=500)
