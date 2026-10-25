
import sqlite3

conn = sqlite3.connect("students.db")
cursor = conn.cursor()

# Create students table
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    section TEXT NOT NULL
)
""")

# Recreate the sample records each time this file runs
cursor.execute("DELETE FROM students")

students = [
    ("2026-00123", "JONARD ALIPALA", "BSIT", 3, "HAMILTON"),
    ("2026-00124", "IAN AUSTRIA", "BSIT", 3, "HAMILTON"),
    ("2026-00125", "RENEIR CALBRO", "BSIT", 3, "HAMILTON"),
    ("2026-00126", "JOH MARK ALARBA", "BSIT", 3, "HAMILTON"),
    ("2026-00127", "JOHN MICHAEL BAUSTISTA", "BSIT", 3, "HAMILTON")
]

# Insert student records
cursor.executemany("""
INSERT INTO students (student_id, name, program, year, section)
VALUES (?, ?, ?, ?, ?)
""", students)

conn.commit()
conn.close()

print("Database created successfully.")
