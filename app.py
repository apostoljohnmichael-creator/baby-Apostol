import os
import sqlite3
import requests
from pathlib import Path
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "students.db"

PARTNER_API_URL = os.environ.get(
    "PARTNER_API_URL",
    "https://jasminerose-2.onrender.com/api/students"
).rstrip("/")

FIELDS = ("student_id", "name", "program", "year", "section")


def ensure_database():
    conn = sqlite3.connect(str(DATABASE), timeout=20)
    try:
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
        columns = [row[1] for row in conn.execute("PRAGMA table_info(students)").fetchall()]
        if "source" not in columns:
            conn.execute("ALTER TABLE students ADD COLUMN source TEXT DEFAULT 'Local'")
        conn.execute("UPDATE students SET source='Local' WHERE source IS NULL OR TRIM(source)=''")

        if conn.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0:
            conn.executemany(
                """
                INSERT INTO students (student_id, name, program, year, section, source)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    ("2026-00123", "JONARD ALIPALA", "BSIT", 3, "HAMILTON", "Local"),
                    ("2026-00124", "IAN AUSTRIA", "BSIT", 3, "HAMILTON", "Local"),
                    ("2026-00125", "RENEIR CALBRO", "BSIT", 3, "HAMILTON", "Local"),
                    ("2026-00126", "JOH MARK ALARBA", "BSIT", 3, "HAMILTON", "Local"),
                    ("2026-00127", "JOHN MICHAEL BAUSTISTA", "BSIT", 3, "HAMILTON", "Local"),
                ],
            )
        conn.commit()
    finally:
        conn.close()


ensure_database()


def get_db_connection():
    conn = sqlite3.connect(str(DATABASE), timeout=20)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def validate_student(data):
    if not isinstance(data, dict):
        return None, "Send a valid JSON object."
    cleaned = {}
    for field in FIELDS:
        value = data.get(field)
        if value is None or str(value).strip() == "":
            return None, f"{field.replace('_', ' ').title()} is required."
        cleaned[field] = str(value).strip()
    try:
        cleaned["year"] = int(cleaned["year"])
        if cleaned["year"] < 1:
            return None, "Year must be a positive number."
    except (ValueError, TypeError):
        return None, "Year must be a number."
    return cleaned, None


def rows_as_dicts(rows):
    return [dict(row) for row in rows]


@app.get("/")
def home():
    return render_template("index.html", partner_api_url=PARTNER_API_URL)


@app.get("/hello")
def hello():
    name = request.args.get("name", "Student").strip() or "Student"
    return jsonify({"message": f"Hello, {name}! Welcome to StudentHub."})


@app.get("/student")
def student_sample():
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT * FROM students ORDER BY id ASC LIMIT 1").fetchone()
        if row is None:
            return jsonify(error="No student record found."), 404
        return jsonify(dict(row))
    finally:
        conn.close()


@app.get("/health")
def health():
    return jsonify(status="success", message="STUDENTHUB API is running")


@app.get("/students")
def get_students():
    conn = get_db_connection()
    try:
        return jsonify(rows_as_dicts(conn.execute(
            "SELECT * FROM students ORDER BY id DESC"
        ).fetchall()))
    finally:
        conn.close()


@app.get("/students/<int:student_id>")
def get_student(student_id):
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()
        if row is None:
            return jsonify(error="Student not found"), 404
        return jsonify(dict(row))
    finally:
        conn.close()


@app.get("/students/program/<string:program>")
def get_students_by_program(program):
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM students WHERE LOWER(program)=LOWER(?) ORDER BY id DESC",
            (program,)
        ).fetchall()
        return jsonify(rows_as_dicts(rows))
    finally:
        conn.close()


@app.get("/students/year/<int:year>")
def get_students_by_year(year):
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM students WHERE year=? ORDER BY id DESC", (year,)
        ).fetchall()
        return jsonify(rows_as_dicts(rows))
    finally:
        conn.close()


@app.get("/students/section/<string:section>")
def get_students_by_section(section):
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM students WHERE LOWER(section)=LOWER(?) ORDER BY id DESC",
            (section,)
        ).fetchall()
        return jsonify(rows_as_dicts(rows))
    finally:
        conn.close()


@app.get("/api/students")
def api_get_students():
    conn = get_db_connection()
    try:
        rows = conn.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
        return jsonify(rows_as_dicts(rows))
    finally:
        conn.close()


@app.post("/api/students")
def api_add_student():
    payload = request.get_json(silent=True)
    data, error = validate_student(payload)
    if error:
        return jsonify(error=error), 400
    source = str((payload or {}).get("source") or "External API").strip()
    conn = get_db_connection()
    try:
        cur = conn.execute("""
            INSERT INTO students (student_id,name,program,year,section,source)
            VALUES (?,?,?,?,?,?)
        """, (*[data[k] for k in FIELDS], source))
        conn.commit()
        return jsonify(message="Student added successfully.", id=cur.lastrowid), 201
    except sqlite3.IntegrityError as exc:
        conn.rollback()
        return jsonify(error=str(exc)), 409
    except sqlite3.Error as exc:
        conn.rollback()
        return jsonify(error=str(exc)), 500
    finally:
        conn.close()


@app.route("/api/students/<int:student_id>", methods=["GET", "PUT", "DELETE"])
def api_student_detail(student_id):
    if request.method == "GET":
        conn = get_db_connection()
        try:
            row = conn.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()
            if row is None:
                return jsonify(error="Student not found"), 404
            return jsonify(dict(row))
        finally:
            conn.close()

    if request.method == "DELETE":
        conn = get_db_connection()
        try:
            cur = conn.execute("DELETE FROM students WHERE id=?", (student_id,))
            if cur.rowcount == 0:
                return jsonify(error="Student not found"), 404
            conn.commit()
            return jsonify(message="Student deleted successfully.")
        except sqlite3.Error as exc:
            conn.rollback()
            return jsonify(error=str(exc)), 500
        finally:
            conn.close()

    payload = request.get_json(silent=True)
    data, error = validate_student(payload)
    if error:
        return jsonify(error=error), 400
    conn = get_db_connection()
    try:
        cur = conn.execute("""
            UPDATE students SET student_id=?, name=?, program=?, year=?, section=?
            WHERE id=?
        """, (*[data[k] for k in FIELDS], student_id))
        if cur.rowcount == 0:
            return jsonify(error="Student not found"), 404
        conn.commit()
        return jsonify(message="Student updated successfully.")
    except sqlite3.Error as exc:
        conn.rollback()
        return jsonify(error=str(exc)), 500
    finally:
        conn.close()


@app.get("/api/students/search")
def search_students():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify(error="Enter a name or student ID."), 400
    conn = get_db_connection()
    try:
        rows = conn.execute("""
            SELECT * FROM students
            WHERE student_id LIKE ? OR name LIKE ? OR program LIKE ?
            ORDER BY id DESC
        """, (f"%{q}%", f"%{q}%", f"%{q}%")).fetchall()
        return jsonify(rows_as_dicts(rows))
    finally:
        conn.close()


@app.get("/partner-records")
def partner_records():
    api_url = request.args.get("api_url", PARTNER_API_URL).strip() or PARTNER_API_URL
    try:
        response = requests.get(api_url, timeout=25)
        response.raise_for_status()
        records = response.json()
        if not isinstance(records, list):
            return jsonify(error="Partner API must return a JSON list.", details=records), 502
        return jsonify(records)
    except requests.RequestException as exc:
        return jsonify(error="Could not connect to the partner API. Check the partner URL and deployment.", details=str(exc)), 502
    except ValueError:
        return jsonify(error="Partner API returned invalid JSON."), 502


@app.post("/import-student")
def import_student():
    data, error = validate_student(request.get_json(silent=True))
    if error:
        return jsonify(error=error), 400
    conn = get_db_connection()
    try:
        cur = conn.execute("""
            INSERT INTO students (student_id,name,program,year,section,source)
            VALUES (?,?,?,?,?,?)
        """, (*[data[k] for k in FIELDS], "Classmate API"))
        conn.commit()
        return jsonify(message="Partner record imported successfully.", id=cur.lastrowid, source="Classmate API"), 201
    except sqlite3.Error as exc:
        conn.rollback()
        return jsonify(error=str(exc)), 500
    finally:
        conn.close()


@app.post("/send-to-partner")
def send_to_partner():
    payload = request.get_json(silent=True) or {}
    api_url = payload.get("api_url", PARTNER_API_URL).strip() or PARTNER_API_URL
    data, error = validate_student(payload)
    if error:
        return jsonify(error=error), 400
    record = {**data, "source": "Partner API"}
    try:
        response = requests.post(api_url, json=record, timeout=25)
        try:
            partner_result = response.json()
        except ValueError:
            partner_result = {"response": response.text[:400]}
        if not response.ok:
            return jsonify(error="Partner rejected the record.", partner_status=response.status_code,
                           partner_response=partner_result), 502
        return jsonify(message="Record successfully sent to partner.", partner_status=response.status_code,
                       partner_response=partner_result), 200
    except requests.RequestException as exc:
        return jsonify(error="Unable to send record to partner.", details=str(exc)), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
