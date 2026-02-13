"""
Script to import students and teams from CSV into the Django database.
Clears all existing teams/students first, then imports from CSV.
"""
import os
import sys
import csv
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.utils import timezone
from tracker.models import Team, Student, AttendanceLog

CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        'Attendance (RF ID) - Sheet1.csv')

def import_csv():
    # Clear existing data first for a clean import
    print(f"Existing teams: {Team.objects.count()}, students: {Student.objects.count()}")
    AttendanceLog.objects.all().delete()
    Student.objects.all().delete()
    Team.objects.all().delete()
    print("Cleared existing data.\n")

    teams_created = 0
    students_created = 0
    errors = []
    team_cache = {}
    now = timezone.now()

    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # skip header row

        current_team_name = None

        for row_num, row in enumerate(reader, start=2):
            if len(row) < 4:
                continue

            team_col = row[0].strip()
            name = row[1].strip()
            reg_no = row[2].strip()
            rfid = row[3].strip()

            # Update current team if team column is filled
            if team_col:
                current_team_name = team_col

            if not current_team_name or not name or not rfid:
                errors.append(f"Row {row_num}: Missing data - team={current_team_name}, name={name}, rfid={rfid}")
                continue

            # Get or create team - set created_at manually, bypass full_clean
            if current_team_name not in team_cache:
                team = Team(team_name=current_team_name, created_at=now)
                team.save_base(raw=True)
                team_cache[current_team_name] = team
                teams_created += 1
                print(f"  Created team: {current_team_name}")
            team = team_cache[current_team_name]

            # Check if student with this RFID already exists
            if Student.objects.filter(rfid_uid=rfid).exists():
                print(f"  Skipped (RFID exists): {name} ({rfid})")
                continue

            # Create student - set registered_at manually, bypass full_clean
            student = Student(name=name, rfid_uid=rfid, team=team, registered_at=now)
            student.save_base(raw=True)
            students_created += 1

            # Mark team as complete if it now has 6 students
            if team.students.count() == 6:
                team.is_complete = True
                team.save_base(raw=True)

    print(f"\n=== Import Summary ===")
    print(f"Teams created: {teams_created}")
    print(f"Students created: {students_created}")
    print(f"Total teams in DB: {Team.objects.count()}")
    print(f"Total students in DB: {Student.objects.count()}")
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")

if __name__ == '__main__':
    print("Importing CSV data into the database...\n")
    import_csv()
    print("\nDone!")
