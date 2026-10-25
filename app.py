
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


# Get all students
@app.route("/students")
def get_students():
    try:
        conn = get_db_connection()
        students = conn.execute(
            "SELECT * FROM students ORDER BY id"
        ).fetchall()
        conn.close()

        return jsonify([dict(student) for student in students])

    except sqlite3.Error as error:
        return jsonify({
            "error": "Database error",
            "message": str(error)
        }), 500


# Get one student by ID
@app.route("/students/<int:id>")
def get_student_by_id(id):
    try:
        conn = get_db_connection()
        student = conn.execute(
            "SELECT * FROM students WHERE id = ?",
            (id,)
        ).fetchone()
        conn.close()

        if student is None:
            return jsonify({"error": "Student not found"}), 404

        return jsonify(dict(student))

    except sqlite3.Error as error:
        return jsonify({
            "error": "Database error",
            "message": str(error)
        }), 500


# Get students by program
@app.route("/students/program/<string:program>")
def get_students_by_program(program):
    try:
        conn = get_db_connection()
        students = conn.execute(
            "SELECT * FROM students WHERE LOWER(program) = LOWER(?)",
            (program,)
        ).fetchall()
        conn.close()

        return jsonify([dict(student) for student in students])

    except sqlite3.Error as error:
        return jsonify({
            "error": "Database error",
            "message": str(error)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
