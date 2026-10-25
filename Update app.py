
import sqlite3
from flask import Flask, jsonify, render_template

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# API: Get all students
@app.route("/students")
def get_students():
    conn = get_db_connection()
    students = conn.execute(
        "SELECT * FROM students ORDER BY id"
    ).fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])


# API: Get one student by database ID
@app.route("/students/<int:id>")
def get_student_by_id(id):
    conn = get_db_connection()
    student = conn.execute(
        "SELECT * FROM students WHERE id = ?", (id,)
    ).fetchone()
    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))


# Additional task: Get students by program
@app.route("/students/program/<string:program>")
def get_students_by_program(program):
    conn = get_db_connection()
    students = conn.execute(
        "SELECT * FROM students WHERE LOWER(program) = LOWER(?)",
        (program,)
    ).fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
