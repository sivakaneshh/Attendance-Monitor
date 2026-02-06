# 📱 RFID Team-Based Event Attendance System

A Django-based backend system for managing team registrations and tracking attendance using RFID cards. Perfect for events, competitions, and team-based activities.

## 🌟 Features

### Phase 1: Registration
- ✅ Create up to 25 teams
- ✅ Register exactly 6 students per team
- ✅ Map unique RFID cards to students
- ✅ Automatic team completion tracking
- ✅ Duplicate prevention (RFID uniqueness)

### Phase 2: Attendance
- ✅ RFID-only check-in/check-out
- ✅ Automatic status toggling (IN → OUT → IN → OUT)
- ✅ Real-time attendance logging
- ✅ Historical attendance tracking
- ✅ Team-wide attendance reports

## 🗄️ Database Schema

```
Teams (25 max)
├── id
├── team_name (unique)
├── is_complete (boolean)
└── created_at

Students (150 max: 25 teams × 6 students)
├── id
├── name
├── rfid_uid (unique, indexed)
├── team_id → Teams
└── registered_at

AttendanceLogs (unlimited)
├── id
├── student_id → Students
├── team_id → Teams
├── status (IN/OUT)
├── check_in_time
├── check_out_time
└── created_at
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Django 5.2.5
- SQLite (included)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Attendance-Monitor
```

2. **Install dependencies**
```bash
pip install django==5.2.5
```

3. **Navigate to project directory**
```bash
cd attendance
```

4. **Apply migrations** (already completed)
```bash
python manage.py migrate
```

5. **Create superuser for admin access**
```bash
python manage.py createsuperuser
```

6. **Run development server**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Complete API documentation is available in [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

### Quick Reference

#### Registration APIs
```
POST /api/teams                    - Create team
POST /api/students/register        - Register student
```

#### Attendance APIs
```
POST /api/attendance/tap           - RFID tap (check-in/out)
```

#### Admin Query APIs
```
GET  /api/teams/list               - List all teams
GET  /api/teams/<id>               - Get team details
GET  /api/attendance/team/<id>     - Team attendance history
GET  /api/attendance/student/<id>  - Student attendance history
GET  /api/status                   - System statistics
```

## 💡 Usage Examples

### 1. Complete Registration Flow

```python
import requests

BASE_URL = "http://localhost:8000"

# Step 1: Create a team
response = requests.post(f"{BASE_URL}/api/teams", json={
    "team_name": "Team Alpha"
})
team = response.json()
team_id = team['id']

# Step 2: Register 6 students
students_data = [
    {"name": "John Doe", "rfid": "RFID001"},
    {"name": "Jane Smith", "rfid": "RFID002"},
    {"name": "Bob Johnson", "rfid": "RFID003"},
    {"name": "Alice Williams", "rfid": "RFID004"},
    {"name": "Charlie Brown", "rfid": "RFID005"},
    {"name": "Diana Prince", "rfid": "RFID006"}
]

for student in students_data:
    response = requests.post(f"{BASE_URL}/api/students/register", json={
        "team_id": team_id,
        "student_name": student["name"],
        "rfid_uid": student["rfid"]
    })
    print(f"Registered: {response.json()}")

# Team is now complete!
```

### 2. Track Attendance

```python
# Simulate RFID taps
rfid_card = "RFID001"

# 1st tap - Check IN
response = requests.post(f"{BASE_URL}/api/attendance/tap", json={
    "rfid_uid": rfid_card
})
print(response.json())  # Status: IN

# 2nd tap - Check OUT
response = requests.post(f"{BASE_URL}/api/attendance/tap", json={
    "rfid_uid": rfid_card
})
print(response.json())  # Status: OUT
```

### 3. Query Attendance

```python
# Get team attendance
team_id = 1
response = requests.get(f"{BASE_URL}/api/attendance/team/{team_id}")
print(response.json())

# Get student attendance
student_id = 1
response = requests.get(f"{BASE_URL}/api/attendance/student/{student_id}")
print(response.json())

# Get system status
response = requests.get(f"{BASE_URL}/api/status")
print(response.json())
```

## 🛡️ Validation Rules

### Team Creation
- ❌ Cannot exceed 25 teams
- ❌ Team names must be unique
- ✅ Teams start as incomplete

### Student Registration
- ❌ RFID must be globally unique
- ❌ Cannot add more than 6 students to a team
- ❌ Student must belong to a valid team
- ✅ Team auto-completes when 6th student added

### Attendance Tracking
- ❌ Cannot tap unregistered RFID
- ✅ Status automatically toggles
- ✅ Preserves complete attendance history
- ✅ Server timestamps used

## 🎯 Business Logic

### Team Completion
```python
# Automatic behavior when 6th student is registered:
if team.students.count() == 6:
    team.is_complete = True
    team.save()
```

### Attendance Toggle
```python
# Tap behavior logic:
last_log = AttendanceLog.objects.filter(student=student).last()

if last_log is None or last_log.status == 'OUT':
    new_status = 'IN'  # Check IN
else:
    new_status = 'OUT'  # Check OUT
```

## 🔧 Project Structure

```
attendance/
├── manage.py                    # Django management script
├── db.sqlite3                   # SQLite database
├── attendance/                  # Project configuration
│   ├── settings.py             # Django settings
│   ├── urls.py                 # Main URL routing
│   └── wsgi.py                 # WSGI application
└── tracker/                     # Main application
    ├── models.py               # Database models (Team, Student, AttendanceLog)
    ├── views.py                # API endpoints
    ├── utils.py                # Business logic & validation
    ├── urls.py                 # API URL routing
    ├── admin.py                # Django admin configuration
    └── migrations/             # Database migrations
        └── 0001_initial.py     # Initial schema
```

## 🔐 Admin Panel

Access the Django admin panel at `http://localhost:8000/admin/`

Features:
- View all teams and completion status
- Browse registered students
- View attendance logs (read-only)
- Search and filter capabilities

**Note:** Manual creation of attendance logs is disabled. Use RFID tap endpoint.

## 📊 System Statistics

Use the `/api/status` endpoint to get:
- Total teams created
- Complete vs incomplete teams
- Total registered students
- Total attendance logs
- System capacity (25 teams, 6 students/team)

## 🧪 Testing

### Manual Testing with cURL

```bash
# Create team
curl -X POST http://localhost:8000/api/teams \
  -H "Content-Type: application/json" \
  -d '{"team_name": "Test Team"}'

# Register student
curl -X POST http://localhost:8000/api/students/register \
  -H "Content-Type: application/json" \
  -d '{"team_id": 1, "student_name": "Test Student", "rfid_uid": "TEST001"}'

# RFID tap
curl -X POST http://localhost:8000/api/attendance/tap \
  -H "Content-Type: application/json" \
  -d '{"rfid_uid": "TEST001"}'

# Get system status
curl http://localhost:8000/api/status
```

### Testing with Python

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete Python examples.

## 🔄 Workflow

### Registration Phase (One-time)
```
1. Admin creates team → POST /api/teams
2. Student taps RFID → (admin reads UID)
3. Admin enters name → POST /api/students/register
4. Repeat steps 2-3 for 6 students
5. Team auto-completes ✓
```

### Attendance Phase (Ongoing)
```
1. Student taps RFID → POST /api/attendance/tap
2. System identifies student + team
3. System toggles IN/OUT status
4. Timestamp recorded
5. History preserved ✓
```

## 🚨 Common Errors & Solutions

### Error: "RFID already registered"
**Cause:** Attempting to register duplicate RFID  
**Solution:** Each RFID must be unique. Check existing registrations.

### Error: "Team already has 6 students"
**Cause:** Trying to add 7th student  
**Solution:** Create a new team or use a different team.

### Error: "RFID not registered in the system"
**Cause:** Tapping unregistered RFID  
**Solution:** Register the student first via `/api/students/register`

### Error: "Maximum of 25 teams already reached"
**Cause:** System limit reached  
**Solution:** Cannot create more teams. Consider archiving old teams.

## 📝 Development Notes

### Key Design Decisions

1. **No User Authentication on Students:** Students are identified solely by RFID, not user accounts.

2. **Server-Side Timestamps:** All timestamps are generated server-side to ensure consistency.

3. **Immutable Attendance History:** Logs are never deleted or modified, only new ones are created.

4. **Auto-Team Completion:** Teams automatically mark as complete when reaching 6 students.

5. **CSRF Exempt APIs:** For ease of integration. Add proper authentication in production.

### Production Considerations

Before deploying to production:

1. **Add Authentication:**
   - JWT tokens for API access
   - Admin authentication for registration endpoints
   - RBAC (Role-Based Access Control)

2. **Enable CSRF Protection:**
   - Remove `@csrf_exempt` decorators
   - Implement proper CSRF token handling

3. **Database:**
   - Migrate from SQLite to PostgreSQL/MySQL
   - Set up proper database backups

4. **Security:**
   - Use environment variables for secrets
   - Enable HTTPS
   - Implement rate limiting
   - Add input sanitization

5. **Monitoring:**
   - Set up logging
   - Add error tracking (e.g., Sentry)
   - Monitor API performance

## 🤝 Contributing

This is a self-contained project. To extend functionality:

1. Add new API endpoints in `tracker/views.py`
2. Update URL routing in `tracker/urls.py`
3. Add business logic in `tracker/utils.py`
4. Create migrations: `python manage.py makemigrations`
5. Apply migrations: `python manage.py migrate`

## 📄 License

This project is provided as-is for educational and event management purposes.

## 📞 Support

For issues and questions:
- Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for detailed API usage
- Review validation rules in `tracker/utils.py`
- Examine models in `tracker/models.py`

---

**Built with Django 5.2.5**  
**Last Updated:** February 6, 2026

🎯 **System Status:** Ready for production use after security hardening
