from django.urls import path
from . import views

urlpatterns = [
    path('', views.attendance, name='attendance'),  # Attendance marking page
    path('login/', views.login_view, name='login'),  # Login page
    path('logout/', views.logout_view, name='logout'),  # Logout
    path('dashboard/', views.dashboard, name='dashboard'),  # Statistics dashboard
    path('register/', views.register_student, name='register_student'),  # Student registration
]