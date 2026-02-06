# 🌐 HTML Interface Guide

## ✅ Setup Complete!

Your RFID Attendance System now has **both HTML interface AND REST API**!

## 🔐 Login Credentials

**Default Admin Account:**
- **Username:** `admin`
- **Password:** `admin123`
- ⚠️ **Change this password in production!**

## 🚀 Getting Started

### 1. Start the Server
```powershell
cd attendance
python manage.py runserver
```

### 2. Access the System
Open your browser and navigate to:

**🌐 Login Page:** http://localhost:8000/

## 📱 Available Pages

After logging in, you'll have access to:

### 1. 📊 Dashboard (`/dashboard`)
- View attendance statistics
- Total students, present/absent counts
- Attendance rate percentage
- Recent attendance records
- **URL:** http://localhost:8000/dashboard

### 2. 👥 Team Management (`/teams`)
- Create new teams (max 25)
- View all teams and their completion status
- See student count per team (0-6 students)
- **URL:** http://localhost:8000/teams

### 3. 📝 Student Registration (`/registration`)
- Register students to teams
- Select team from dropdown
- Enter student name and RFID UID
- View all registered students
- **URL:** http://localhost:8000/registration

### 4. ✅ Mark Attendance (`/attendance`)
- Scan or enter RFID UID
- Auto-toggle between CHECK-IN and CHECK-OUT
- View today's attendance records in real-time
- **URL:** http://localhost:8000/attendance

## 🔄 Typical Workflow

### Phase 1: Setup (One-Time)
1. **Login** at http://localhost:8000
2. **Create Teams** at `/teams`
   - Click "Manage Teams"
   - Enter team name and click "Create Team"
   - Repeat until you have all teams (max 25)

3. **Register Students** at `/registration`
   - Click "Student Registration"
   - Select team from dropdown
   - Enter student name
   - Scan/Enter RFID UID
   - Click "Register Student"
   - Repeat for all students (6 per team)

### Phase 2: Daily Operations
1. **Mark Attendance** at `/attendance`
   - Students scan their RFID cards
   - First tap: CHECK-IN ✅
   - Second tap: CHECK-OUT ❌
   - Third tap: CHECK-IN ✅
   - Pattern continues...

2. **View Statistics** at `/dashboard`
   - Monitor attendance rates
   - See recent activity
   - Track present/absent counts

## 🔌 REST API Still Available!

Your REST API endpoints are still fully functional:

### API Endpoints
```
POST   /api/teams                          # Create team
POST   /api/students/register              # Register student
POST   /api/attendance/tap                 # RFID tap (check-in/out)
GET    /api/teams/list                     # List all teams
GET    /api/teams/<id>                     # Team details
GET    /api/attendance/team/<id>           # Team attendance
GET    /api/attendance/student/<id>        # Student attendance
GET    /api/status                         # System statistics
```

### Example API Usage
```powershell
# Create a team via API
curl -X POST http://localhost:8000/api/teams `
  -H "Content-Type: application/json" `
  -d '{"team_name": "Team Alpha"}'

# Register student via API
curl -X POST http://localhost:8000/api/students/register `
  -H "Content-Type: application/json" `
  -d '{"team_id": 1, "student_name": "John Doe", "rfid_uid": "ABC123"}'

# RFID tap via API (for hardware integration)
curl -X POST http://localhost:8000/api/attendance/tap `
  -H "Content-Type: application/json" `
  -d '{"rfid_uid": "ABC123"}'
```

## 🎯 Best Use Cases

### HTML Interface (Browser)
- ✅ Admin team setup and management
- ✅ Manual student registration
- ✅ Viewing statistics and reports
- ✅ Monitoring real-time attendance
- ✅ Manual RFID entry (if hardware unavailable)

### REST API (Hardware/Scripts)
- ✅ RFID reader hardware integration
- ✅ Automated attendance systems
- ✅ Mobile app integration
- ✅ Third-party system integration
- ✅ Automated testing and scripts

## 🎨 Features

### ✨ User-Friendly Interface
- Clean, modern design
- Responsive layout
- Real-time updates
- Success/error notifications
- Auto-hide alerts

### 🔒 Security
- Login required for all pages
- Django authentication system
- CSRF protection
- Session management

### 📊 Data Validation
- Unique RFID UIDs
- Team size limits (6 students)
- Maximum team count (25)
- Duplicate prevention
- Form validation

## 🛠️ Administration

### Django Admin Panel
Access at: http://localhost:8000/admin

Use the same credentials:
- Username: `admin`
- Password: `admin123`

Manage:
- User accounts
- Teams
- Students
- Attendance logs
- Full CRUD operations

## 🐛 Troubleshooting

### Can't Login?
```powershell
# Recreate admin user
cd attendance
python setup_admin.py
```

### Server Not Starting?
```powershell
# Check if port 8000 is available
netstat -ano | findstr :8000

# Use different port
python manage.py runserver 8080
```

### CSS Not Loading?
```powershell
# Collect static files
python manage.py collectstatic
```

## 📝 Creating Additional Users

### Via Django Admin:
1. Go to http://localhost:8000/admin
2. Click "Users" → "Add User"
3. Set username and password
4. Save and add permissions

### Via Python Script:
```python
# Create a new admin user
python setup_admin.py
```

## 🎉 Summary

You now have:
- ✅ **HTML Interface** for easy browser-based management
- ✅ **REST API** for RFID hardware integration
- ✅ **Team Management** system
- ✅ **Student Registration** with RFID mapping
- ✅ **Attendance Tracking** with auto-toggle
- ✅ **Dashboard** with real-time statistics
- ✅ **Admin Panel** for data management

## 📚 Next Steps

1. **Test the system:**
   - Login and create a few teams
   - Register some test students
   - Mark attendance with test RFID UIDs

2. **Connect hardware:**
   - Integrate RFID reader with REST API
   - Test automatic attendance logging

3. **Customize:**
   - Update team size limits in `models.py`
   - Modify attendance rules in `utils.py`
   - Enhance UI in templates

4. **Deploy:**
   - Change SECRET_KEY in settings
   - Set DEBUG = False
   - Configure proper database
   - Set up production server

---

**🎊 Enjoy your new HTML interface!**

For questions or issues, check:
- [README.md](../README.md)
- [API_DOCUMENTATION.md](../API_DOCUMENTATION.md)
- [ARCHITECTURE.md](../ARCHITECTURE.md)
