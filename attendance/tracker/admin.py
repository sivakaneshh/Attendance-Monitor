# tracker/admin.py
"""
Django Admin configuration for RFID Team-Based Event Attendance System
"""
from django.contrib import admin
from .models import Team, Student, AttendanceLog


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin interface for Team model."""
    list_display = ('team_name', 'is_complete', 'get_student_count', 'created_at')
    list_filter = ('is_complete', 'created_at')
    search_fields = ('team_name',)
    readonly_fields = ('is_complete', 'created_at')
    
    def get_student_count(self, obj):
        """Display student count in list view."""
        return obj.students.count()
    get_student_count.short_description = 'Student Count'


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin interface for Student model."""
    list_display = ('name', 'rfid_uid', 'team', 'registered_at')
    list_filter = ('team', 'registered_at')
    search_fields = ('name', 'rfid_uid', 'team__team_name')
    readonly_fields = ('registered_at',)
    
    def get_readonly_fields(self, request, obj=None):
        """Make RFID and team read-only after creation."""
        if obj:  # Editing an existing object
            return self.readonly_fields + ('rfid_uid', 'team')
        return self.readonly_fields


@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    """Admin interface for AttendanceLog model."""
    list_display = ('student', 'team', 'status', 'check_in_time', 'check_out_time', 'created_at')
    list_filter = ('status', 'team', 'created_at')
    search_fields = ('student__name', 'student__rfid_uid', 'team__team_name')
    readonly_fields = ('created_at', 'check_in_time', 'check_out_time')
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        """Disable manual creation of attendance logs (should be created via RFID tap)."""
        return False

