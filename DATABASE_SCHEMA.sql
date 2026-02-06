-- ============================================================================
-- RFID TEAM-BASED EVENT ATTENDANCE SYSTEM - SQL SCHEMA
-- ============================================================================
-- Database: SQLite3
-- Django Version: 5.2.5
-- Generated: February 6, 2026
-- ============================================================================

-- ============================================================================
-- TABLE: tracker_team
-- Description: Stores team information (max 25 teams)
-- ============================================================================
CREATE TABLE "tracker_team" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "team_name" VARCHAR(100) NOT NULL UNIQUE,
    "is_complete" BOOLEAN NOT NULL,
    "created_at" DATETIME NOT NULL
);

-- Index for faster team name lookups
CREATE INDEX "tracker_team_team_name_idx" ON "tracker_team" ("team_name");

-- ============================================================================
-- TABLE: tracker_student
-- Description: Stores student information (max 150 students: 25 teams × 6)
-- ============================================================================
CREATE TABLE "tracker_student" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" VARCHAR(200) NOT NULL,
    "rfid_uid" VARCHAR(100) NOT NULL UNIQUE,
    "team_id" INTEGER NOT NULL REFERENCES "tracker_team" ("id") 
        ON DELETE CASCADE 
        DEFERRABLE INITIALLY DEFERRED,
    "registered_at" DATETIME NOT NULL
);

-- Index for ultra-fast RFID lookups (critical for tap operations)
CREATE INDEX "tracker_student_rfid_uid_idx" ON "tracker_student" ("rfid_uid");

-- Index for team-based queries
CREATE INDEX "tracker_student_team_id_idx" ON "tracker_student" ("team_id");

-- ============================================================================
-- TABLE: tracker_attendancelog
-- Description: Stores check-in/check-out logs (unlimited records)
-- ============================================================================
CREATE TABLE "tracker_attendancelog" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "student_id" INTEGER NOT NULL REFERENCES "tracker_student" ("id") 
        ON DELETE CASCADE 
        DEFERRABLE INITIALLY DEFERRED,
    "team_id" INTEGER NOT NULL REFERENCES "tracker_team" ("id") 
        ON DELETE CASCADE 
        DEFERRABLE INITIALLY DEFERRED,
    "status" VARCHAR(3) NOT NULL CHECK ("status" IN ('IN', 'OUT')),
    "check_in_time" DATETIME NULL,
    "check_out_time" DATETIME NULL,
    "created_at" DATETIME NOT NULL
);

-- Index for student attendance history queries
CREATE INDEX "tracker_attendancelog_student_id_idx" 
    ON "tracker_attendancelog" ("student_id");

-- Index for team attendance history queries
CREATE INDEX "tracker_attendancelog_team_id_idx" 
    ON "tracker_attendancelog" ("team_id");

-- Index for chronological sorting (most recent first)
CREATE INDEX "tracker_attendancelog_created_at_idx" 
    ON "tracker_attendancelog" ("created_at" DESC);

-- Composite index for efficient student+date queries
CREATE INDEX "tracker_attendancelog_student_created_idx" 
    ON "tracker_attendancelog" ("student_id", "created_at" DESC);

-- ============================================================================
-- SAMPLE DATA INSERTS
-- ============================================================================

-- Insert sample teams
INSERT INTO "tracker_team" ("team_name", "is_complete", "created_at") VALUES
    ('Team Alpha', 1, '2026-02-06 10:00:00'),
    ('Team Beta', 0, '2026-02-06 10:15:00'),
    ('Team Gamma', 1, '2026-02-06 10:30:00');

-- Insert sample students for Team Alpha (complete team)
INSERT INTO "tracker_student" ("name", "rfid_uid", "team_id", "registered_at") VALUES
    ('John Doe', 'RFID001', 1, '2026-02-06 10:05:00'),
    ('Jane Smith', 'RFID002', 1, '2026-02-06 10:06:00'),
    ('Bob Johnson', 'RFID003', 1, '2026-02-06 10:07:00'),
    ('Alice Williams', 'RFID004', 1, '2026-02-06 10:08:00'),
    ('Charlie Brown', 'RFID005', 1, '2026-02-06 10:09:00'),
    ('Diana Prince', 'RFID006', 1, '2026-02-06 10:10:00');

-- Insert sample students for Team Beta (incomplete team)
INSERT INTO "tracker_student" ("name", "rfid_uid", "team_id", "registered_at") VALUES
    ('Peter Parker', 'RFID007', 2, '2026-02-06 10:20:00'),
    ('Mary Jane', 'RFID008', 2, '2026-02-06 10:21:00'),
    ('Bruce Wayne', 'RFID009', 2, '2026-02-06 10:22:00');

-- Insert sample attendance logs (demonstrating toggle behavior)
INSERT INTO "tracker_attendancelog" 
    ("student_id", "team_id", "status", "check_in_time", "check_out_time", "created_at") 
VALUES
    -- John Doe's attendance
    (1, 1, 'IN', '2026-02-06 14:00:00', NULL, '2026-02-06 14:00:00'),
    (1, 1, 'OUT', NULL, '2026-02-06 18:00:00', '2026-02-06 18:00:00'),
    
    -- Jane Smith's attendance
    (2, 1, 'IN', '2026-02-06 14:05:00', NULL, '2026-02-06 14:05:00'),
    (2, 1, 'OUT', NULL, '2026-02-06 17:45:00', '2026-02-06 17:45:00'),
    
    -- Bob Johnson's attendance
    (3, 1, 'IN', '2026-02-06 14:10:00', NULL, '2026-02-06 14:10:00');

-- ============================================================================
-- USEFUL QUERIES
-- ============================================================================

-- Query 1: Get all complete teams with student count
SELECT 
    t.id,
    t.team_name,
    t.is_complete,
    COUNT(s.id) as student_count,
    t.created_at
FROM tracker_team t
LEFT JOIN tracker_student s ON t.id = s.team_id
GROUP BY t.id
HAVING t.is_complete = 1;

-- Query 2: Get students of a specific team
SELECT 
    s.id,
    s.name,
    s.rfid_uid,
    s.registered_at
FROM tracker_student s
WHERE s.team_id = 1
ORDER BY s.registered_at;

-- Query 3: Get latest attendance status for each student
SELECT 
    s.id as student_id,
    s.name,
    s.rfid_uid,
    t.team_name,
    al.status as current_status,
    al.created_at as last_tap_time
FROM tracker_student s
JOIN tracker_team t ON s.team_id = t.id
LEFT JOIN tracker_attendancelog al ON al.id = (
    SELECT id 
    FROM tracker_attendancelog 
    WHERE student_id = s.id 
    ORDER BY created_at DESC 
    LIMIT 1
)
ORDER BY s.team_id, s.name;

-- Query 4: Get attendance history for a specific student
SELECT 
    al.id,
    al.status,
    al.check_in_time,
    al.check_out_time,
    al.created_at
FROM tracker_attendancelog al
WHERE al.student_id = 1
ORDER BY al.created_at DESC;

-- Query 5: Get team attendance summary for today
SELECT 
    t.team_name,
    COUNT(DISTINCT al.student_id) as students_present,
    COUNT(al.id) as total_taps
FROM tracker_team t
LEFT JOIN tracker_attendancelog al ON t.id = al.team_id
WHERE DATE(al.created_at) = DATE('now')
GROUP BY t.id
ORDER BY t.team_name;

-- Query 6: Find students currently checked in (last status = IN)
SELECT 
    s.id,
    s.name,
    s.rfid_uid,
    t.team_name,
    al.created_at as check_in_time
FROM tracker_student s
JOIN tracker_team t ON s.team_id = t.id
JOIN tracker_attendancelog al ON al.id = (
    SELECT id 
    FROM tracker_attendancelog 
    WHERE student_id = s.id 
    ORDER BY created_at DESC 
    LIMIT 1
)
WHERE al.status = 'IN'
ORDER BY al.created_at DESC;

-- Query 7: System statistics
SELECT 
    (SELECT COUNT(*) FROM tracker_team) as total_teams,
    (SELECT COUNT(*) FROM tracker_team WHERE is_complete = 1) as complete_teams,
    (SELECT COUNT(*) FROM tracker_team WHERE is_complete = 0) as incomplete_teams,
    (SELECT COUNT(*) FROM tracker_student) as total_students,
    (SELECT COUNT(*) FROM tracker_attendancelog) as total_attendance_logs,
    (SELECT COUNT(DISTINCT student_id) FROM tracker_attendancelog 
     WHERE DATE(created_at) = DATE('now')) as students_active_today;

-- ============================================================================
-- CONSTRAINTS & BUSINESS RULES VALIDATION
-- ============================================================================

-- Check 1: Verify no team has more than 6 students
SELECT 
    t.team_name,
    COUNT(s.id) as student_count
FROM tracker_team t
LEFT JOIN tracker_student s ON t.id = s.team_id
GROUP BY t.id
HAVING COUNT(s.id) > 6;
-- Should return 0 rows

-- Check 2: Verify RFID uniqueness
SELECT 
    rfid_uid,
    COUNT(*) as count
FROM tracker_student
GROUP BY rfid_uid
HAVING COUNT(*) > 1;
-- Should return 0 rows

-- Check 3: Verify teams marked complete have exactly 6 students
SELECT 
    t.team_name,
    t.is_complete,
    COUNT(s.id) as student_count
FROM tracker_team t
LEFT JOIN tracker_student s ON t.id = s.team_id
WHERE t.is_complete = 1
GROUP BY t.id
HAVING COUNT(s.id) != 6;
-- Should return 0 rows

-- Check 4: Verify all attendance logs have valid student and team references
SELECT COUNT(*) as orphaned_logs
FROM tracker_attendancelog al
LEFT JOIN tracker_student s ON al.student_id = s.id
LEFT JOIN tracker_team t ON al.team_id = t.id
WHERE s.id IS NULL OR t.id IS NULL;
-- Should return 0

-- ============================================================================
-- PERFORMANCE OPTIMIZATION NOTES
-- ============================================================================
-- 1. RFID lookups are indexed for O(log n) performance
-- 2. Foreign keys use CASCADE for automatic cleanup
-- 3. Composite indexes for common query patterns
-- 4. LIMIT 1 used in subqueries for last status lookups
-- 5. Created_at DESC index for chronological queries

-- ============================================================================
-- MAINTENANCE QUERIES
-- ============================================================================

-- Archive old attendance logs (example: older than 1 year)
-- DELETE FROM tracker_attendancelog 
-- WHERE created_at < DATE('now', '-1 year');

-- Reset all teams (WARNING: DELETES ALL DATA)
-- DELETE FROM tracker_attendancelog;
-- DELETE FROM tracker_student;
-- DELETE FROM tracker_team;

-- Vacuum database to reclaim space after deletions
-- VACUUM;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
