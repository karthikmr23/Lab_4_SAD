from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DATABASE = os.path.join(
    os.path.dirname(__file__),
    "../database/department.db"
)


def get_db():
    return sqlite3.connect(DATABASE)


def initialize_database():
    db = get_db()

    db.execute("""
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        department_name TEXT NOT NULL,
        officer_name TEXT NOT NULL,
        ward TEXT NOT NULL,
        contact TEXT NOT NULL,
        complaint_type TEXT NOT NULL
    )
    """)

    db.commit()
    db.close()


# Add a department
@app.route("/departments", methods=["POST"])
def create_department():

    data = request.json

    department_name = data["department_name"]
    officer_name = data["officer_name"]
    ward = data["ward"]
    contact = data["contact"]
    complaint_type = data["complaint_type"].lower().strip()

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    INSERT INTO departments
    (department_name, officer_name, ward, contact, complaint_type)
    VALUES (?, ?, ?, ?, ?)
    """, (
        department_name,
        officer_name,
        ward,
        contact,
        complaint_type
    ))

    db.commit()

    department_id = cursor.lastrowid

    db.close()

    return jsonify({
        "department_id": department_id,
        "department_name": department_name,
        "officer_name": officer_name,
        "ward": ward,
        "contact": contact,
        "complaint_type": complaint_type
    }), 201


# Find department by ID
@app.route("/departments/<int:department_id>", methods=["GET"])
def get_department(department_id):

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    SELECT
        id,
        department_name,
        officer_name,
        ward,
        contact,
        complaint_type
    FROM departments
    WHERE id = ?
    """, (department_id,))

    department = cursor.fetchone()

    db.close()

    if department is None:
        return jsonify({
            "error": "Department not found"
        }), 404

    return jsonify({
        "department_id": department[0],
        "department_name": department[1],
        "officer_name": department[2],
        "ward": department[3],
        "contact": department[4],
        "complaint_type": department[5]
    })


# Find department based on complaint type
@app.route("/departments/by-type/<complaint_type>", methods=["GET"])
def get_department_by_type(complaint_type):

    complaint_type = complaint_type.lower().strip()

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    SELECT
        id,
        department_name,
        officer_name,
        ward,
        contact,
        complaint_type
    FROM departments
    WHERE complaint_type = ?
    LIMIT 1
    """, (complaint_type,))

    department = cursor.fetchone()

    db.close()

    if department is None:
        return jsonify({
            "error": "No department found for this complaint type"
        }), 404

    return jsonify({
        "department_id": department[0],
        "department_name": department[1],
        "officer_name": department[2],
        "ward": department[3],
        "contact": department[4],
        "complaint_type": department[5]
    })


if __name__ == "__main__":
    initialize_database()
    app.run(port=5003, debug=True)
