from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import requests

app = Flask(__name__)
CORS(app)

DATABASE = os.path.join(
    os.path.dirname(__file__),
    "../database/complaint.db"
)

CITIZEN_SERVICE_URL = "http://localhost:5001"
DEPARTMENT_SERVICE_URL = "http://localhost:5003"


def get_db():
    return sqlite3.connect(DATABASE)


def initialize_database():
    db = get_db()

    db.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        citizen_id INTEGER NOT NULL,
        complaint_type TEXT NOT NULL,
        description TEXT NOT NULL,
        location TEXT NOT NULL,
        department TEXT,
        officer TEXT,
        status TEXT NOT NULL
    )
    """)

    # Add new columns if an older database already exists
    columns = [
        row[1]
        for row in db.execute(
            "PRAGMA table_info(complaints)"
        ).fetchall()
    ]

    if "complaint_type" not in columns:
        db.execute(
            "ALTER TABLE complaints "
            "ADD COLUMN complaint_type TEXT DEFAULT 'general'"
        )

    if "department" not in columns:
        db.execute(
            "ALTER TABLE complaints "
            "ADD COLUMN department TEXT"
        )

    if "officer" not in columns:
        db.execute(
            "ALTER TABLE complaints "
            "ADD COLUMN officer TEXT"
        )

    db.commit()
    db.close()


@app.route("/complaints", methods=["POST"])
def create_complaint():

    data = request.json

    citizen_id = data["citizen_id"]
    complaint_type = data["complaint_type"].lower().strip()
    description = data["description"]
    location = data["location"]

    # 1. Verify citizen
    try:
        citizen_response = requests.get(
            f"{CITIZEN_SERVICE_URL}/citizens/{citizen_id}",
            timeout=3
        )
    except requests.exceptions.RequestException:
        return jsonify({
            "error": "Citizen Service is unavailable"
        }), 503

    if citizen_response.status_code == 404:
        return jsonify({
            "error": "Citizen does not exist"
        }), 400

    if citizen_response.status_code != 200:
        return jsonify({
            "error": "Unable to verify citizen"
        }), 500

    citizen = citizen_response.json()

    # 2. Find the correct department and officer
    try:
        department_response = requests.get(
            f"{DEPARTMENT_SERVICE_URL}/departments/by-type/{complaint_type}",
            timeout=3
        )
    except requests.exceptions.RequestException:
        return jsonify({
            "error": "Department Service is unavailable"
        }), 503

    if department_response.status_code != 200:
        return jsonify({
            "error": "No department found for this complaint type"
        }), 400

    department = department_response.json()

    department_name = department["department_name"]
    officer_name = department["officer_name"]

    # 3. Store complaint
    status = "OPEN"

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    INSERT INTO complaints
    (
        citizen_id,
        complaint_type,
        description,
        location,
        department,
        officer,
        status
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        citizen_id,
        complaint_type,
        description,
        location,
        department_name,
        officer_name,
        status
    ))

    db.commit()
    complaint_id = cursor.lastrowid
    db.close()

    # 4. Return complete result
    return jsonify({
        "complaint_id": complaint_id,
        "citizen_id": citizen_id,
        "citizen_name": citizen["name"],
        "complaint_type": complaint_type,
        "description": description,
        "location": location,
        "department": department_name,
        "officer": officer_name,
        "status": status
    }), 201


@app.route("/complaints/<int:complaint_id>", methods=["GET"])
def get_complaint(complaint_id):

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    SELECT
        id,
        citizen_id,
        complaint_type,
        description,
        location,
        department,
        officer,
        status
    FROM complaints
    WHERE id = ?
    """, (complaint_id,))

    complaint = cursor.fetchone()
    db.close()

    if complaint is None:
        return jsonify({
            "error": "Complaint not found"
        }), 404

    return jsonify({
        "complaint_id": complaint[0],
        "citizen_id": complaint[1],
        "complaint_type": complaint[2],
        "description": complaint[3],
        "location": complaint[4],
        "department": complaint[5],
        "officer": complaint[6],
        "status": complaint[7]
    })


@app.route("/complaints", methods=["GET"])
def get_all_complaints():

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    SELECT
        id,
        citizen_id,
        complaint_type,
        description,
        location,
        department,
        officer,
        status
    FROM complaints
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    db.close()

    complaints = []

    for row in rows:
        complaints.append({
            "complaint_id": row[0],
            "citizen_id": row[1],
            "complaint_type": row[2],
            "description": row[3],
            "location": row[4],
            "department": row[5],
            "officer": row[6],
            "status": row[7]
        })

    return jsonify(complaints)


@app.route("/complaints/citizen/<int:citizen_id>", methods=["GET"])
def get_complaints_by_citizen(citizen_id):

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    SELECT
        id,
        citizen_id,
        complaint_type,
        description,
        location,
        department,
        officer,
        status
    FROM complaints
    WHERE citizen_id = ?
    ORDER BY id DESC
    """, (citizen_id,))

    rows = cursor.fetchall()
    db.close()

    complaints = []

    for row in rows:
        complaints.append({
            "complaint_id": row[0],
            "citizen_id": row[1],
            "complaint_type": row[2],
            "description": row[3],
            "location": row[4],
            "department": row[5],
            "officer": row[6],
            "status": row[7]
        })

    return jsonify(complaints)


@app.route("/complaints/<int:complaint_id>/status", methods=["PUT"])
def update_status(complaint_id):

    data = request.json
    new_status = data.get("status")

    allowed_statuses = [
        "OPEN",
        "ASSIGNED",
        "IN PROGRESS",
        "RESOLVED",
        "REJECTED"
    ]

    if new_status not in allowed_statuses:
        return jsonify({
            "error": "Invalid status"
        }), 400

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    UPDATE complaints
    SET status = ?
    WHERE id = ?
    """, (new_status, complaint_id))

    db.commit()

    if cursor.rowcount == 0:
        db.close()
        return jsonify({
            "error": "Complaint not found"
        }), 404

    db.close()

    return jsonify({
        "message": "Complaint status updated",
        "complaint_id": complaint_id,
        "status": new_status
    })


if __name__ == "__main__":
    initialize_database()
    app.run(port=5002, debug=True)
