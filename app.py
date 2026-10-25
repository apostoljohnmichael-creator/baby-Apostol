
import sqlite3
from flask import Flask, jsonify, request, render_template

app = Flask(__name__, template_folder=".")


# Database connection
def get_db_connection():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Student Information API
@app.route("/student")
def get_student():
    student = {
        "student_id": "2026-00123",
        "name": "John Michieal Apostol",
        "program": "BSIT",
        "year": 3,
        "section": "A"
    }
    return jsonify(student)


# Greeting API
@app.route("/hello")
def say_hello():
    name = request.args.get("name", "Student").strip()
    if not name:
        name = "Student"
    return jsonify({"message": f"Hello, {name}!"})


# Health check endpoint
@app.route("/health")
def health():
    return jsonify({
        "status": "success",
        "message": "Flask API is running."
    })


# Get all students - existing route
@app.route("/students")
def get_students():
    conn = get_db_connection()
    try:
        students = conn.execute(
            "SELECT * FROM students ORDER BY id"
        ).fetchall()
        return jsonify([dict(student) for student in students])
    except sqlite3.Error as error:
        return jsonify({"error": str(error)}), 500
    finally:
        conn.close()


# Get one student by ID - existing route
@app.route("/students/<int:id>")
def get_student_by_id(id):
    conn = get_db_connection()
    try:
        student = conn.execute(
            "SELECT * FROM students WHERE id = ?", (id,)
        ).fetchone()

        if student is None:
            return jsonify({"error": "Student not found"}), 404

        return jsonify(dict(student))
    except sqlite3.Error as error:
        return jsonify({"error": str(error)}), 500
    finally:
        conn.close()


# Get students by program - existing route
@app.route("/students/program/<string:program>")
def get_students_by_program(program):
    conn = get_db_connection()
    try:
        students = conn.execute(
            "SELECT * FROM students WHERE LOWER(program) = LOWER(?)",
            (program,)
        ).fetchall()
        return jsonify([dict(student) for student in students])
    except sqlite3.Error as error:
        return jsonify({"error": str(error)}), 500
    finally:
        conn.close()


# CRUD API: Get all students
@app.route("/api/students", methods=["GET"])
def api_get_students():
    conn = get_db_connection()
    try:
        students = conn.execute(
            "SELECT * FROM students ORDER BY id DESC"
        ).fetchall()
        return jsonify([dict(student) for student in students])
    except sqlite3.Error as error:
        return jsonify({"error": str(error)}), 500
    finally:
        conn.close()


# CRUD API: Add student
@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON data"}), 400

    fields = ["student_id", "name", "program", "year", "section"]

    if any(
        data.get(field) is None or str(data.get(field)).strip() == ""
        for field in fields
    ):
        return jsonify({"error": "All student fields are required"}), 400

    conn = get_db_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO students
            (student_id, name, program, year, section)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                str(data["student_id"]).strip(),
                str(data["name"]).strip(),
                str(data["program"]).strip(),
                str(data["year"]).strip(),
                str(data["section"]).strip()
            )
        )
        conn.commit()

        return jsonify({
            "message": "Student added successfully",
            "id": cursor.lastrowid
        }), 201

    except sqlite3.IntegrityError:
        conn.rollback()
        return jsonify({
            "error": "Could not add student. The student ID may already exist."
        }), 409
    except sqlite3.Error as error:
        conn.rollback()
        return jsonify({"error": str(error)}), 500
    finally:
        conn.close()


# CRUD API: Get one student
@app.route("/api/students/<int:id>", methods=["GET"])
def api_get_student_by_id(id):
    conn = get_db_connection()
    try:
        student = conn.execute(
            "SELECT * FROM students WHERE id = ?", (id,)
        ).fetchone()

        if student is None:
            return jsonify({"error": "Student not found"}), 404

        return jsonify(dict(student))
    except sqlite3.Error as error:
        return jsonify({"error": str(error)}), 500
    finally:
        conn.close()


# CRUD API: Update student
@app.route("/api/students/<int:id>", methods=["PUT"])
def update_student(id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON data"}), 400

    fields = ["student_id", "name", "program", "year", "section"]

    if any(
        data.get(field) is None or str(data.get(field)).strip() == ""
        for field in fields
    ):
        return jsonify({"error": "All student fields are required"}), 400

    conn = get_db_connection()
    try:
        cursor = conn.execute(
            """
            UPDATE students
            SET student_id = ?, name = ?, program = ?, year = ?, section = ?
            WHERE id = ?
            """,
            (
                str(data["student_id"]).strip(),
                str(data["name"]).strip(),
                str(data["program"]).strip(),
                str(data["year"]).strip(),
                str(data["section"]).strip(),
                id
            )
        )

        if cursor.rowcount == 0:
            conn.rollback()
            return jsonify({"error": "Student not found"}), 404

        conn.commit()
        return jsonify({"message": "Student updated successfully"})

    except sqlite3.IntegrityError:
        conn.rollback()
        return jsonify({
            "error": "Could not update student. The student ID may already exist."
        }), 409
    except sqlite3.Error as error:
        conn.rollback()
        return jsonify({"error": str(error)}), 500
    finally:
        conn.close()


# CRUD API: Delete student
@app.route("/api/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM students WHERE id = ?", (id,)
        )

        if cursor.rowcount == 0:
            conn.rollback()
            return jsonify({"error": "Student not found"}), 404

        conn.commit()
        return jsonify({"message": "Student deleted successfully"})

    except sqlite3.Error as error:
        conn.rollback()
        return jsonify({"error": str(error)}), 500
    finally:
        conn.close()

# SEARCH students by student ID or name
@app.route("/api/students/search", methods=["GET"])
def search_students():
    keyword = request.args.get("q", "").strip()

    if not keyword:
        return jsonify({
            "error": "Please enter a student name or ID"
        }), 400

    conn = get_db_connection()

    try:
        students = conn.execute(
            """
            SELECT * FROM students
            WHERE student_id LIKE ? OR name LIKE ?
            ORDER BY id
            """,
            (f"%{keyword}%", f"%{keyword}%")
        ).fetchall()

        return jsonify([dict(student) for student in students])

    except sqlite3.Error as error:
        return jsonify({
            "error": "Database error",
            "message": str(error)
        }), 500

    finally:
        conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
