from django.urls import path
from . import views

"""
URL Configuration for RFID Team-Based Event Attendance System

HTML Interface Pages:
- GET/POST /                          - Login page
- GET      /logout                     - Logout
- GET      /dashboard                  - Dashboard with statistics
- GET/POST /registration               - Student registration page
- GET/POST /attendance                 - Attendance marking page

API Endpoints:

PHASE 1 - REGISTRATION:
- POST /api/teams                      - Create team
- POST /api/students/register          - Register student to team

PHASE 2 - ATTENDANCE:
- POST /api/attendance/tap             - Process RFID tap (check-in/out)

ADMIN QUERIES:
- GET  /api/teams                      - List all teams
- GET  /api/teams/<id>                 - Get team details
- GET  /api/attendance/team/<id>       - Get team attendance history
- GET  /api/attendance/student/<id>    - Get student attendance history
- GET  /api/status                     - System status and statistics
"""

urlpatterns = [
    # ========================================================================
    # HTML INTERFACE PAGES
    # ========================================================================
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/download-csv/', views.download_attendance_csv, name='download_attendance_csv'),
    path('teams/', views.team_management_page, name='teams'),
    path('registration/', views.registration_page, name='register_student'),
    path('attendance/', views.attendance_page, name='attendance'),
    
    # ========================================================================
    # PHASE 1: TEAM REGISTRATION (API)
    # ========================================================================
    path('api/teams', views.create_team, name='create_team'),
    path('api/students/register', views.register_student, name='register_student_api'),
    
    # ========================================================================
    # PHASE 2: ATTENDANCE TRACKING (API)
    # ========================================================================
    path('api/attendance/tap', views.rfid_tap, name='rfid_tap'),
    
    # ========================================================================
    # ADMIN QUERIES (API)
    # ========================================================================
    path('api/teams/list', views.list_teams, name='list_teams'),
    path('api/teams/<int:team_id>', views.get_team_detail, name='get_team_detail'),
    path('api/attendance/team/<int:team_id>', views.get_team_attendance, name='get_team_attendance'),
    path('api/attendance/student/<int:student_id>', views.get_student_attendance, name='get_student_attendance'),
    
    # ========================================================================
    # SYSTEM STATUS (API)
    # ========================================================================
    path('api/status', views.system_status, name='system_status'),
]
