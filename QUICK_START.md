# 🚀 Quick Start Guide - RFID Attendance System

## ⚡ 5-Minute Setup

### Step 1: Start the Server
```bash
cd c:\Users\sksiv\Documents\GitHub\Attendance-Monitor\attendance
python manage.py runserver
```

✅ Server running at: **http://localhost:8000**

---

## 🧪 Test the System (Copy & Paste These Commands)

### Test 1: Check System Status
```bash
curl http://localhost:8000/api/status
```

### Test 2: Create a Team
```bash
curl -X POST http://localhost:8000/api/teams ^
  -H "Content-Type: application/json" ^
  -d "{\"team_name\": \"Team Alpha\"}"
```

### Test 3: Register a Student
```bash
curl -X POST http://localhost:8000/api/students/register ^
  -H "Content-Type: application/json" ^
  -d "{\"team_id\": 1, \"student_name\": \"John Doe\", \"rfid_uid\": \"RFID001\"}"
```

### Test 4: RFID Check-In
```bash
curl -X POST http://localhost:8000/api/attendance/tap ^
  -H "Content-Type: application/json" ^
  -d "{\"rfid_uid\": \"RFID001\"}"
```

### Test 5: RFID Check-Out
```bash
curl -X POST http://localhost:8000/api/attendance/tap ^
  -H "Content-Type: application/json" ^
  -d "{\"rfid_uid\": \"RFID001\"}"
```

### Test 6: View Attendance
```bash
curl http://localhost:8000/api/attendance/student/1
```

---

## 🐍 Python Quick Test

```python
import requests

BASE = "http://localhost:8000"

# 1. Create Team
team = requests.post(f"{BASE}/api/teams", 
                     json={"team_name": "Team Alpha"}).json()
print("Team:", team)

# 2. Register Student
student = requests.post(f"{BASE}/api/students/register", json={
    "team_id": team['id'],
    "student_name": "John Doe",
    "rfid_uid": "RFID001"
}).json()
print("Student:", student)

# 3. Check-In
tap1 = requests.post(f"{BASE}/api/attendance/tap", 
                     json={"rfid_uid": "RFID001"}).json()
print("Check-IN:", tap1)

# 4. Check-Out
tap2 = requests.post(f"{BASE}/api/attendance/tap", 
                     json={"rfid_uid": "RFID001"}).json()
print("Check-OUT:", tap2)
```

---

## 🎯 Complete Workflow Demo

Run the automated test script:
```bash
cd c:\Users\sksiv\Documents\GitHub\Attendance-Monitor
python test_system.py
```

This will:
- ✅ Create 3 teams
- ✅ Register 6 students to one team
- ✅ Test validation rules
- ✅ Simulate RFID taps
- ✅ Query attendance data
- ✅ Show system statistics

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | Complete API reference |
| [SYSTEM_README.md](SYSTEM_README.md) | Full setup guide |
| [DATABASE_SCHEMA.sql](DATABASE_SCHEMA.sql) | Database structure |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Project overview |

---

## 🔐 Admin Panel

1. **Create an admin user:**
```bash
cd c:\Users\sksiv\Documents\GitHub\Attendance-Monitor\attendance
python manage.py createsuperuser
```

2. **Access admin panel:**  
   Visit: **http://localhost:8000/admin/**

---

## 📋 API Endpoints Reference

### Registration (Phase 1)
```
POST /api/teams                     → Create team
POST /api/students/register         → Register student
```

### Attendance (Phase 2)
```
POST /api/attendance/tap            → RFID tap (IN/OUT)
```

### Queries (Admin)
```
GET  /api/teams/list                → List all teams
GET  /api/teams/<id>                → Team details
GET  /api/attendance/team/<id>      → Team attendance
GET  /api/attendance/student/<id>   → Student attendance
GET  /api/status                    → System stats
```

---

## 🎯 Next Steps

1. ✅ **Run the test script** to see everything in action
2. ✅ **Try the API endpoints** with curl or Postman
3. ✅ **Access the admin panel** to view data
4. ✅ **Build your frontend** using the API
5. ✅ **Read the docs** for detailed information

---

## 🆘 Troubleshooting

### Server won't start?
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Run migrations
python manage.py migrate
```

### API returns 404?
- Make sure server is running
- Check the URL path (include `/api/`)
- Verify endpoint in [urls.py](attendance/tracker/urls.py)

### Need to reset database?
```bash
# Delete database
del db.sqlite3

# Re-create
python manage.py migrate
```

---

## 💡 Key Concepts

### Team Registration
- Create team → Register 6 students → Team auto-completes

### Attendance Tracking
- RFID tap → System identifies student → Toggle IN/OUT → Save log

### Data Flow
```
RFID Tap → Find Student → Get Last Status → Toggle → Create Log
```

---

**Ready to go! Start with `python manage.py runserver` and explore! 🚀**
