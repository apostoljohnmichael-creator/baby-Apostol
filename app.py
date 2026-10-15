
from flask import Flask, jsonify, request, render_template

app = Flask(__name__, template_folder=".")


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

    return jsonify({
        "message": f"Hello, {name}!"
    })


# Health check endpoint
@app.route("/health")
def health():
    return jsonify({
        "status": "success",
        "message": "Flask API is running."
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
