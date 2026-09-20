from flask import Flask, jsonify, request

app = Flask(__name__)


# 1. Home
@app.route('/')
def home():
    return "Welcome to John Michael Apostol's API! sir success!"


# 2. Student Information
@app.route('/student')
def get_student():
    return jsonify({
        "student_id": "24-00188",
        "name": "John Michael Apostol",
        "program": "BSIT",
        "year": 3,
        "section": "hamilton"
    })


# 3. Greeting
@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'John Michael Apostol')

    return jsonify({
        "message": f"Hello, {name}!"
    })


# Run the Flask application
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
