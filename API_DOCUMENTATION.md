# RFID Team-Based Event Attendance System - API Documentation

## 📋 Table of Contents
- [Overview](#overview)
- [System Rules](#system-rules)
- [Database Schema](#database-schema)
- [Phase 1: Team Registration APIs](#phase-1-team-registration-apis)
- [Phase 2: Attendance Tracking APIs](#phase-2-attendance-tracking-apis)
- [Admin Query APIs](#admin-query-apis)
- [Error Handling](#error-handling)
- [Testing Examples](#testing-examples)

---

## Overview

This system manages team-based event attendance using RFID cards with two distinct phases:

1. **Phase 1: Registration** - One-time team and student registration
2. **Phase 2: Attendance** - Ongoing RFID-based check-in/check-out tracking

---

## System Rules

### 🎯 Core Constraints

| Rule | Value |
|------|-------|
| **Total Teams** | Maximum 25 |
| **Students per Team** | Exactly 6 |
| **RFID Cards** | Unique per student |
| **Registration** | One-time only |
| **Attendance** | RFID-only (no names) |

### 📊 Attendance Logic

| Tap # | Action |
|-------|--------|
| 1st   | CHECK-IN |
| 2nd   | CHECK-OUT |
| 3rd   | CHECK-IN |
| 4th   | CHECK-OUT |

The system automatically toggles between IN and OUT status on each tap.

---

## Database Schema

### Team Model
```python
{
    "id": Integer (Primary Key),
    "team_name": String (Unique),
    "is_complete": Boolean,
    "created_at": DateTime
}
```

### Student Model
```python
{
    "id": Integer (Primary Key),
    "name": String,
    "rfid_uid": String (Unique, Indexed),
    "team_id": Foreign Key → Team,
    "registered_at": DateTime
}
```

### AttendanceLog Model
```python
{
    "id": Integer (Primary Key),
    "student_id": Foreign Key → Student,
    "team_id": Foreign Key → Team,
    "status": String ("IN" or "OUT"),
    "check_in_time": DateTime (nullable),
    "check_out_time": DateTime (nullable),
    "created_at": DateTime
}
```

---

## Phase 1: Team Registration APIs

### 1.1 Create Team

**Endpoint:** `POST /api/teams`

**Description:** Create a new team for registration.

**Request Body:**
```json
{
    "team_name": "Team Alpha"
}
```

**Success Response (201):**
```json
{
    "id": 1,
    "team_name": "Team Alpha",
    "is_complete": false,
    "student_count": 0,
    "created_at": "2026-02-06T10:30:00Z"
}
```

**Error Responses:**
- **400 Bad Request:** `team_name is required`
- **400 Bad Request:** `Maximum of 25 teams already reached.`
- **400 Bad Request:** Team name already exists (duplicate)

**Validation Rules:**
- ❌ Cannot create more than 25 teams
- ❌ Team name must be unique
- ✅ Team starts incomplete (0 students)

---

### 1.2 Register Student

**Endpoint:** `POST /api/students/register`

**Description:** Register a student to a team with their RFID card.

**Request Body:**
```json
{
    "team_id": 1,
    "student_name": "John Doe",
    "rfid_uid": "ABC123XYZ"
}
```

**Success Response (201):**
```json
{
    "id": 1,
    "name": "John Doe",
    "rfid_uid": "ABC123XYZ",
    "team": {
        "id": 1,
        "team_name": "Team Alpha",
        "is_complete": false,
        "student_count": 1
    },
    "registered_at": "2026-02-06T10:35:00Z"
}
```

**When 6th Student is Added:**
```json
{
    "id": 6,
    "name": "Jane Smith",
    "rfid_uid": "XYZ789DEF",
    "team": {
        "id": 1,
        "team_name": "Team Alpha",
        "is_complete": true,
        "student_count": 6
    },
    "registered_at": "2026-02-06T11:00:00Z"
}
```

**Error Responses:**
- **400 Bad Request:** `team_id is required`
- **400 Bad Request:** `student_name is required`
- **400 Bad Request:** `rfid_uid is required`
- **400 Bad Request:** `RFID 'ABC123XYZ' is already registered.`
- **400 Bad Request:** `Team 'Team Alpha' already has 6 students.`
- **400 Bad Request:** `Team with ID 99 does not exist.`

**Validation Rules:**
- ❌ RFID must be globally unique
- ❌ Team cannot exceed 6 students
- ❌ Cannot register to non-existent team
- ✅ Team auto-completes when 6th student added

---

## Phase 2: Attendance Tracking APIs

### 2.1 RFID Tap (Check-In/Out)

**Endpoint:** `POST /api/attendance/tap`

**Description:** Process an RFID tap to toggle attendance status.

**Request Body:**
```json
{
    "rfid_uid": "ABC123XYZ"
}
```

**Success Response - First Tap (Check-IN) (200):**
```json
{
    "message": "Attendance logged: IN",
    "attendance_log": {
        "id": 1,
        "student_id": 1,
        "student_name": "John Doe",
        "team_id": 1,
        "team_name": "Team Alpha",
        "status": "IN",
        "timestamp": "2026-02-06T14:00:00Z",
        "check_in_time": "2026-02-06T14:00:00Z",
        "check_out_time": null
    }
}
```

**Success Response - Second Tap (Check-OUT) (200):**
```json
{
    "message": "Attendance logged: OUT",
    "attendance_log": {
        "id": 2,
        "student_id": 1,
        "student_name": "John Doe",
        "team_id": 1,
        "team_name": "Team Alpha",
        "status": "OUT",
        "timestamp": "2026-02-06T18:00:00Z",
        "check_in_time": null,
        "check_out_time": "2026-02-06T18:00:00Z"
    }
}
```

**Error Responses:**
- **400 Bad Request:** `rfid_uid is required`
- **400 Bad Request:** `RFID 'UNKNOWN123' is not registered in the system.`

**Behavior:**
1. First tap → Creates IN record
2. Second tap → Creates OUT record
3. Third tap → Creates IN record
4. Continues toggling indefinitely

---

## Admin Query APIs

### 3.1 List All Teams

**Endpoint:** `GET /api/teams/list`

**Description:** Get a list of all teams with their status.

**Success Response (200):**
```json
{
    "total_teams": 3,
    "teams": [
        {
            "id": 1,
            "team_name": "Team Alpha",
            "is_complete": true,
            "student_count": 6,
            "created_at": "2026-02-06T10:30:00Z"
        },
        {
            "id": 2,
            "team_name": "Team Beta",
            "is_complete": false,
            "student_count": 4,
            "created_at": "2026-02-06T10:45:00Z"
        },
        {
            "id": 3,
            "team_name": "Team Gamma",
            "is_complete": true,
            "student_count": 6,
            "created_at": "2026-02-06T11:00:00Z"
        }
    ]
}
```

---

### 3.2 Get Team Details

**Endpoint:** `GET /api/teams/<team_id>`

**Description:** Get detailed information about a specific team including all students.

**Example:** `GET /api/teams/1`

**Success Response (200):**
```json
{
    "id": 1,
    "team_name": "Team Alpha",
    "is_complete": true,
    "student_count": 6,
    "created_at": "2026-02-06T10:30:00Z",
    "students": [
        {
            "id": 1,
            "name": "John Doe",
            "rfid_uid": "ABC123XYZ",
            "registered_at": "2026-02-06T10:35:00Z"
        },
        {
            "id": 2,
            "name": "Jane Smith",
            "rfid_uid": "DEF456GHI",
            "registered_at": "2026-02-06T10:40:00Z"
        }
        // ... 4 more students
    ]
}
```

**Error Response:**
- **404 Not Found:** `Team with ID 99 not found`

---

### 3.3 Get Team Attendance History

**Endpoint:** `GET /api/attendance/team/<team_id>`

**Description:** Get all attendance logs for a specific team.

**Example:** `GET /api/attendance/team/1`

**Success Response (200):**
```json
{
    "team_id": 1,
    "team_name": "Team Alpha",
    "total_logs": 12,
    "attendance_logs": [
        {
            "id": 12,
            "student": {
                "id": 2,
                "name": "Jane Smith",
                "rfid_uid": "DEF456GHI"
            },
            "status": "OUT",
            "check_in_time": null,
            "check_out_time": "2026-02-06T18:00:00Z",
            "created_at": "2026-02-06T18:00:00Z"
        },
        {
            "id": 11,
            "student": {
                "id": 1,
                "name": "John Doe",
                "rfid_uid": "ABC123XYZ"
            },
            "status": "OUT",
            "check_in_time": null,
            "check_out_time": "2026-02-06T17:45:00Z",
            "created_at": "2026-02-06T17:45:00Z"
        }
        // ... more logs (ordered by newest first)
    ]
}
```

**Error Response:**
- **404 Not Found:** `Team with ID 99 not found`

---

### 3.4 Get Student Attendance History

**Endpoint:** `GET /api/attendance/student/<student_id>`

**Description:** Get all attendance logs for a specific student.

**Example:** `GET /api/attendance/student/1`

**Success Response (200):**
```json
{
    "student": {
        "id": 1,
        "name": "John Doe",
        "rfid_uid": "ABC123XYZ",
        "team": {
            "id": 1,
            "team_name": "Team Alpha"
        }
    },
    "total_logs": 4,
    "attendance_logs": [
        {
            "id": 4,
            "status": "OUT",
            "check_in_time": null,
            "check_out_time": "2026-02-06T18:00:00Z",
            "created_at": "2026-02-06T18:00:00Z"
        },
        {
            "id": 3,
            "status": "IN",
            "check_in_time": "2026-02-06T14:00:00Z",
            "check_out_time": null,
            "created_at": "2026-02-06T14:00:00Z"
        }
        // ... more logs (ordered by newest first)
    ]
}
```

**Error Response:**
- **404 Not Found:** `Student with ID 99 not found`

---

### 3.5 System Status

**Endpoint:** `GET /api/status`

**Description:** Get system statistics and health status.

**Success Response (200):**
```json
{
    "status": "operational",
    "statistics": {
        "total_teams": 10,
        "complete_teams": 8,
        "incomplete_teams": 2,
        "total_students": 56,
        "total_attendance_logs": 234,
        "max_teams_allowed": 25,
        "students_per_team": 6
    },
    "timestamp": "2026-02-06T20:00:00Z"
}
```

---

## Error Handling

### Standard Error Response Format
```json
{
    "error": "Error message describing what went wrong"
}
```

### HTTP Status Codes

| Code | Meaning | When It Occurs |
|------|---------|----------------|
| 200 | OK | Successful GET or POST (attendance tap) |
| 201 | Created | Successful POST (team/student creation) |
| 400 | Bad Request | Validation error, missing fields, business rule violation |
| 404 | Not Found | Resource (team/student) does not exist |
| 500 | Internal Server Error | Unexpected server error |

---

## Testing Examples

### 🧪 Complete Registration Flow

```bash
# 1. Create Team
curl -X POST http://localhost:8000/api/teams \
  -H "Content-Type: application/json" \
  -d '{"team_name": "Team Alpha"}'

# 2. Register 6 Students
curl -X POST http://localhost:8000/api/students/register \
  -H "Content-Type: application/json" \
  -d '{"team_id": 1, "student_name": "John Doe", "rfid_uid": "RFID001"}'

curl -X POST http://localhost:8000/api/students/register \
  -H "Content-Type: application/json" \
  -d '{"team_id": 1, "student_name": "Jane Smith", "rfid_uid": "RFID002"}'

# ... repeat for 4 more students
# 6th student will auto-complete the team
```

### 🧪 Attendance Tracking Flow

```bash
# 1st Tap - Check IN
curl -X POST http://localhost:8000/api/attendance/tap \
  -H "Content-Type: application/json" \
  -d '{"rfid_uid": "RFID001"}'

# 2nd Tap - Check OUT
curl -X POST http://localhost:8000/api/attendance/tap \
  -H "Content-Type: application/json" \
  -d '{"rfid_uid": "RFID001"}'

# 3rd Tap - Check IN again
curl -X POST http://localhost:8000/api/attendance/tap \
  -H "Content-Type: application/json" \
  -d '{"rfid_uid": "RFID001"}'
```

### 🧪 Query Examples

```bash
# Get all teams
curl http://localhost:8000/api/teams/list

# Get specific team details
curl http://localhost:8000/api/teams/1

# Get team attendance
curl http://localhost:8000/api/attendance/team/1

# Get student attendance
curl http://localhost:8000/api/attendance/student/1

# Get system status
curl http://localhost:8000/api/status
```

---

## 🔐 Security Notes

1. **CSRF Protection:** The `@csrf_exempt` decorator is used for API endpoints. In production, implement proper token-based authentication.

2. **Authentication:** Current implementation has no authentication. Consider adding:
   - JWT tokens for API access
   - Admin authentication for registration endpoints
   - Rate limiting for attendance tapping

3. **Input Validation:** All inputs are validated for:
   - Required fields
   - Data types
   - Business rule compliance

---

## 📚 Additional Resources

- Django Admin Panel: `http://localhost:8000/admin/`
- Models: [tracker/models.py](attendance/tracker/models.py)
- Business Logic: [tracker/utils.py](attendance/tracker/utils.py)
- API Views: [tracker/views.py](attendance/tracker/views.py)

---

**System Version:** 1.0  
**Last Updated:** February 6, 2026  
**Framework:** Django 5.2.5
