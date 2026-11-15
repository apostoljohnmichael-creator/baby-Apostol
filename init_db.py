import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent / "students.db"

seed_students = [
    ("2026-00123", "JONARD ALIPALA", "BSIT", 3, "HAMILTON", "Local"),
    ("2026-00124", "IAN AUSTRIA", "BSIT", 3, "HAMILTON", "Local"),
    ("2026-00125", "RENEIR CALBRO", "BSIT", 3, "HAMILTON", "Local"),
    ("2026-00126", "JOH MARK ALARBA", "BSIT", 3, "HAMILTON", "Local"),
    ("2026-00127", "JOHN MICHAEL BAUSTISTA", "BSIT", 3, "HAMILTON", "Local"),
]

conn = sqlite3.connect(DB)
conn.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    section TEXT NOT NULL,
    source TEXT DEFAULT 'Local'
)
""")

# Safely add source to an older database if it is missing.
columns = [row[1] for row in conn.execute("PRAGMA table_info(students)").fetchall()]
if "source" not in columns:
    conn.execute("ALTER TABLE students ADD COLUMN source TEXT DEFAULT 'Local'")
conn.execute("UPDATE students SET source='Local' WHERE source IS NULL OR TRIM(source)=''")

# Seed only when the table is empty. Existing records are preserved.
count = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
if count == 0:
    conn.executemany("""
        INSERT INTO students (student_id,name,program,year,section,source)
        VALUES (?,?,?,?,?,?)
    """, seed_students)

conn.commit()
conn.close()
print(f"Database ready: {DB}")
