"""
Test Script for RFID Team-Based Event Attendance System

This script demonstrates the complete workflow:
1. Creating teams
2. Registering students
3. Tracking attendance via RFID taps
4. Querying attendance data

Prerequisites:
- Django server running on http://localhost:8000
- Run: python manage.py runserver

Usage:
    python test_system.py
"""

import requests
import json
from datetime import datetime


class AttendanceSystemTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.teams = []
        self.students = []
    
    def print_section(self, title):
        """Print a formatted section header."""
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70)
    
    def print_response(self, response):
        """Pretty print API response."""
        try:
            data = response.json()
            print(f"Status: {response.status_code}")
            print(json.dumps(data, indent=2))
        except:
            print(f"Status: {response.status_code}")
            print(response.text)
    
    def test_create_teams(self):
        """Test creating multiple teams."""
        self.print_section("PHASE 1: CREATING TEAMS")
        
        team_names = ["Team Alpha", "Team Beta", "Team Gamma"]
        
        for team_name in team_names:
            print(f"\n📝 Creating: {team_name}")
            response = requests.post(
                f"{self.base_url}/api/teams",
                json={"team_name": team_name}
            )
            self.print_response(response)
            
            if response.status_code == 201:
                self.teams.append(response.json())
    
    def test_register_students(self):
        """Test registering students to teams."""
        self.print_section("PHASE 2: REGISTERING STUDENTS")
        
        if not self.teams:
            print("❌ No teams available. Create teams first.")
            return
        
        # Register 6 students to the first team
        team_id = self.teams[0]['id']
        team_name = self.teams[0]['team_name']
        
        print(f"\n👥 Registering 6 students to {team_name} (ID: {team_id})")
        
        students_data = [
            {"name": "John Doe", "rfid": "RFID001"},
            {"name": "Jane Smith", "rfid": "RFID002"},
            {"name": "Bob Johnson", "rfid": "RFID003"},
            {"name": "Alice Williams", "rfid": "RFID004"},
            {"name": "Charlie Brown", "rfid": "RFID005"},
            {"name": "Diana Prince", "rfid": "RFID006"}
        ]
        
        for i, student in enumerate(students_data, 1):
            print(f"\n🎫 Student {i}/6: {student['name']} (RFID: {student['rfid']})")
            response = requests.post(
                f"{self.base_url}/api/students/register",
                json={
                    "team_id": team_id,
                    "student_name": student["name"],
                    "rfid_uid": student["rfid"]
                }
            )
            self.print_response(response)
            
            if response.status_code == 201:
                self.students.append(response.json())
                
                # Check if team is complete
                if response.json()['team']['is_complete']:
                    print(f"\n✅ Team '{team_name}' is now COMPLETE with 6 students!")
    
    def test_duplicate_rfid(self):
        """Test duplicate RFID validation."""
        self.print_section("TEST: DUPLICATE RFID VALIDATION")
        
        if not self.teams or not self.students:
            print("❌ Need teams and students first.")
            return
        
        team_id = self.teams[0]['id']
        
        print("\n❌ Attempting to register duplicate RFID 'RFID001'...")
        response = requests.post(
            f"{self.base_url}/api/students/register",
            json={
                "team_id": team_id,
                "student_name": "Duplicate Person",
                "rfid_uid": "RFID001"  # Already registered
            }
        )
        self.print_response(response)
    
    def test_team_overflow(self):
        """Test team capacity validation."""
        self.print_section("TEST: TEAM OVERFLOW VALIDATION")
        
        if not self.teams:
            print("❌ Need teams first.")
            return
        
        team_id = self.teams[0]['id']
        
        print("\n❌ Attempting to add 7th student to full team...")
        response = requests.post(
            f"{self.base_url}/api/students/register",
            json={
                "team_id": team_id,
                "student_name": "Extra Person",
                "rfid_uid": "RFID099"
            }
        )
        self.print_response(response)
    
    def test_attendance_tracking(self):
        """Test RFID tap attendance tracking."""
        self.print_section("PHASE 3: ATTENDANCE TRACKING (RFID TAPS)")
        
        if not self.students:
            print("❌ No students registered.")
            return
        
        # Get first student's RFID
        rfid = self.students[0]['rfid_uid']
        name = self.students[0]['name']
        
        print(f"\n📱 Simulating RFID taps for: {name} ({rfid})")
        
        # Simulate 4 taps
        for tap_num in range(1, 5):
            print(f"\n👆 Tap #{tap_num}")
            response = requests.post(
                f"{self.base_url}/api/attendance/tap",
                json={"rfid_uid": rfid}
            )
            self.print_response(response)
    
    def test_unregistered_rfid(self):
        """Test tapping unregistered RFID."""
        self.print_section("TEST: UNREGISTERED RFID")
        
        print("\n❌ Attempting to tap unregistered RFID 'UNKNOWN999'...")
        response = requests.post(
            f"{self.base_url}/api/attendance/tap",
            json={"rfid_uid": "UNKNOWN999"}
        )
        self.print_response(response)
    
    def test_query_apis(self):
        """Test admin query endpoints."""
        self.print_section("PHASE 4: ADMIN QUERIES")
        
        # List all teams
        print("\n📋 Listing all teams...")
        response = requests.get(f"{self.base_url}/api/teams/list")
        self.print_response(response)
        
        if self.teams:
            team_id = self.teams[0]['id']
            
            # Get team details
            print(f"\n🔍 Getting details for Team ID {team_id}...")
            response = requests.get(f"{self.base_url}/api/teams/{team_id}")
            self.print_response(response)
            
            # Get team attendance
            print(f"\n📊 Getting attendance history for Team ID {team_id}...")
            response = requests.get(f"{self.base_url}/api/attendance/team/{team_id}")
            self.print_response(response)
        
        if self.students:
            student_id = self.students[0]['id']
            
            # Get student attendance
            print(f"\n📊 Getting attendance history for Student ID {student_id}...")
            response = requests.get(f"{self.base_url}/api/attendance/student/{student_id}")
            self.print_response(response)
    
    def test_system_status(self):
        """Test system status endpoint."""
        self.print_section("SYSTEM STATUS")
        
        print("\n💻 Getting system statistics...")
        response = requests.get(f"{self.base_url}/api/status")
        self.print_response(response)
    
    def run_all_tests(self):
        """Run complete test suite."""
        print("\n" + "█"*70)
        print("  RFID TEAM-BASED ATTENDANCE SYSTEM - AUTOMATED TEST")
        print("█"*70)
        print(f"\nBase URL: {self.base_url}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        try:
            # Phase 1: Registration
            self.test_create_teams()
            self.test_register_students()
            
            # Validation tests
            self.test_duplicate_rfid()
            self.test_team_overflow()
            
            # Phase 2: Attendance
            self.test_attendance_tracking()
            self.test_unregistered_rfid()
            
            # Admin queries
            self.test_query_apis()
            self.test_system_status()
            
            # Summary
            self.print_section("TEST SUMMARY")
            print(f"\n✅ Teams Created: {len(self.teams)}")
            print(f"✅ Students Registered: {len(self.students)}")
            print(f"✅ All tests completed successfully!")
            
        except requests.exceptions.ConnectionError:
            print("\n❌ ERROR: Cannot connect to server!")
            print("   Make sure Django server is running:")
            print("   python manage.py runserver")
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")


def main():
    """Main execution function."""
    tester = AttendanceSystemTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
