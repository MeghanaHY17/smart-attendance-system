import sqlite3

DATABASE = "attendance.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            face_file TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def add_student(student_id, name, face_file):
    conn = get_connection()

    conn.execute("""
        INSERT OR REPLACE INTO students
        (id, name, face_file)
        VALUES (?, ?, ?)
    """, (student_id, name, face_file))

    conn.commit()
    conn.close()


def get_students():
    conn = get_connection()

    students = conn.execute("""
        SELECT id, name, face_file
        FROM students
    """).fetchall()

    conn.close()

    return students


def mark_attendance(student_id, name):
    from datetime import datetime

    now = datetime.now()

    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    conn = get_connection()

    existing = conn.execute("""
        SELECT id
        FROM attendance
        WHERE student_id = ?
        AND date = ?
    """, (student_id, date)).fetchone()

    if existing:
        conn.close()
        return False

    conn.execute("""
        INSERT INTO attendance
        (student_id, name, date, time, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        student_id,
        name,
        date,
        time,
        "Present"
    ))

    conn.commit()
    conn.close()

    return True


def get_attendance():
    conn = get_connection()

    records = conn.execute("""
        SELECT student_id, name, date, time, status
        FROM attendance
        ORDER BY date DESC, time DESC
    """).fetchall()

    conn.close()

    return records