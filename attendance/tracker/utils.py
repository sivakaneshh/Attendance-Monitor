# tracker/utils.py
"""
Business logic and validation utilities for RFID team attendance system.
"""
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Team, Student, AttendanceLog


class RFIDHelper:
    """Helper utilities for RFID operations."""

    @staticmethod
    def normalize_rfid(rfid_uid):
        """
        Normalize RFID UID by removing leading zeros.
        
        Examples:
            '0012345' -> '12345'
            '00012345' -> '12345'
            '12345' -> '12345'
            '000' -> '0' (keeps at least one digit)
        
        Args:
            rfid_uid (str): Raw RFID UID from reader
            
        Returns:
            str: Normalized RFID UID without leading zeros
        """
        if not rfid_uid:
            return rfid_uid
        
        # Strip leading zeros but keep at least one character
        normalized = rfid_uid.lstrip('0') or '0'
        return normalized


class TeamValidator:
    """Validation utilities for team operations."""

    @staticmethod
    def validate_team_capacity(team):
        """Check if team can accept more students (max 6)."""
        if team.students.count() >= 6:
            raise ValidationError(f"Team '{team.team_name}' already has 6 students.")

    @staticmethod
    def validate_rfid_unique(rfid_uid, exclude_student_id=None):
        """Check if RFID is already registered."""
        query = Student.objects.filter(rfid_uid=rfid_uid)
        if exclude_student_id:
            query = query.exclude(id=exclude_student_id)
        
        if query.exists():
            raise ValidationError(f"RFID '{rfid_uid}' is already registered.")


class AttendanceService:
    """Business logic for attendance tracking."""

    @staticmethod
    def process_rfid_tap(rfid_uid):
        """
        Process an RFID tap and toggle between CHECK-IN and CHECK-OUT.
        
        Logic:
        - 1st tap: IN
        - 2nd tap: OUT
        - 3rd tap: IN
        - 4th tap: OUT
        ... and so on
        
        Returns:
            dict: Attendance log details with status
        
        Raises:
            ValidationError: If RFID is not registered
        """
        # Normalize RFID UID (remove leading zeros)
        rfid_uid = RFIDHelper.normalize_rfid(rfid_uid)
        
        # Find student by RFID
        try:
            student = Student.objects.select_related('team').get(rfid_uid=rfid_uid)
        except Student.DoesNotExist:
            raise ValidationError(f"RFID '{rfid_uid}' is not registered in the system.")

        # Get the last attendance record for this student
        last_log = AttendanceLog.objects.filter(student=student).order_by('-created_at').first()

        # Determine new status (toggle between IN and OUT)
        if last_log is None or last_log.status == 'OUT':
            new_status = 'IN'
        else:
            new_status = 'OUT'

        # Create new attendance log
        attendance_log = AttendanceLog.objects.create(
            student=student,
            team=student.team,
            status=new_status
        )

        return {
            'id': attendance_log.id,
            'student_id': student.id,
            'student_name': student.name,
            'team_id': student.team.id,
            'team_name': student.team.team_name,
            'status': new_status,
            'timestamp': attendance_log.created_at,
            'check_in_time': attendance_log.check_in_time,
            'check_out_time': attendance_log.check_out_time
        }

    @staticmethod
    def get_student_attendance_history(student_id):
        """Get all attendance logs for a specific student."""
        logs = AttendanceLog.objects.filter(
            student_id=student_id
        ).select_related('student', 'team').order_by('-created_at')

        return logs

    @staticmethod
    def get_team_attendance_history(team_id):
        """Get all attendance logs for a specific team."""
        logs = AttendanceLog.objects.filter(
            team_id=team_id
        ).select_related('student', 'team').order_by('-created_at')

        return logs

    @staticmethod
    def get_live_count():
        """
        Get live count of students currently IN vs OUT.
        
        Logic:
        - Every student is counted exactly once
        - If last status is 'IN', student is counted as IN
        - If last status is 'OUT' or never marked, student is counted as OUT
        - total_students = in_count + out_count (always balanced)
        
        Returns:
            dict: Contains 'in_count', 'out_count', and 'total_students'
        """
        from django.db.models import Subquery, OuterRef
        
        # Get the last attendance log ID for each student
        last_log_subquery = AttendanceLog.objects.filter(
            student=OuterRef('pk')
        ).order_by('-created_at').values('status')[:1]
        
        # Annotate all students with their last attendance status
        students_with_status = Student.objects.annotate(
            last_status=Subquery(last_log_subquery)
        ).values_list('last_status', flat=True)
        
        # Count students by status
        in_count = sum(1 for status in students_with_status if status == 'IN')
        out_count = sum(1 for status in students_with_status if status != 'IN')
        total_students = Student.objects.count()
        
        return {
            'in_count': in_count,
            'out_count': out_count,
            'total_students': total_students
        }


class RegistrationService:
    """Business logic for team and student registration."""

    @staticmethod
    def create_team(team_name):
        """
        Create a new team.
        
        Args:
            team_name (str): Name of the team
            
        Returns:
            Team: Created team instance
            
        Raises:
            ValidationError: If validation fails
        """
        # Create team
        team = Team.objects.create(team_name=team_name)
        return team

    @staticmethod
    def register_student(team_id, student_name, rfid_uid):
        """
        Register a new student to a team.
        
        Args:
            team_id (int): ID of the team
            student_name (str): Name of the student
            rfid_uid (str): RFID card UID
            
        Returns:
            Student: Created student instance
            
        Raises:
            ValidationError: If validation fails
        """
        # Normalize RFID UID (remove leading zeros)
        rfid_uid = RFIDHelper.normalize_rfid(rfid_uid)
        
        # Get team
        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            raise ValidationError(f"Team with ID {team_id} does not exist.")

        # Validate RFID uniqueness
        TeamValidator.validate_rfid_unique(rfid_uid)

        # Validate team capacity
        TeamValidator.validate_team_capacity(team)

        # Create student
        student = Student.objects.create(
            name=student_name,
            rfid_uid=rfid_uid,
            team=team
        )

        # Check if team is now complete (6 students)
        if team.students.count() == 6:
            team.is_complete = True
            team.save()

        return student

