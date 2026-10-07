from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    Response
)

import os
import csv
import io
import base64

from database import (
    create_tables,
    add_student,
    get_students,
    mark_attendance,
    get_attendance
)

from face_utils import (
    save_face,
    recognize_face
)


app = Flask(__name__)

# Create database
create_tables()

# Create faces folder
os.makedirs("faces", exist_ok=True)


# -----------------------------------
# Home page
# -----------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------------
# Register student
# -----------------------------------

@app.route("/register", methods=["POST"])
def register():

    try:

        student_id = request.form.get(
            "student_id",
            ""
        ).strip()

        name = request.form.get(
            "name",
            ""
        ).strip()

        image_data = request.files.get(
            "image"
        )

        if not student_id or not name:

            return jsonify({
                "success": False,
                "message": "Student ID and name are required."
            })

        if image_data is None:

            return jsonify({
                "success": False,
                "message": "Face image is required."
            })

        filename = f"faces/{student_id}.jpg"

        image_bytes = image_data.read()

        success, message = save_face(
            image_bytes,
            filename
        )

        if not success:

            return jsonify({
                "success": False,
                "message": message
            })

        add_student(
            student_id,
            name,
            filename
        )

        return jsonify({
            "success": True,
            "message": f"{name} registered successfully."
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        })


# -----------------------------------
# Recognize face
# -----------------------------------

@app.route("/recognize", methods=["POST"])
def recognize():

    try:

        image = request.files.get(
            "image"
        )

        if image is None:

            return jsonify({
                "success": False,
                "message": "Image not received."
            })

        students = get_students()

        if len(students) == 0:

            return jsonify({
                "success": False,
                "message": "No students registered."
            })

        image_data = image.read()

        result = recognize_face(
            image_data,
            students
        )

        if result["recognized"]:

            marked = mark_attendance(
                result["student_id"],
                result["name"]
            )

            if marked:

                message = (
                    f"Attendance marked for "
                    f"{result['name']}"
                )

            else:

                message = (
                    f"{result['name']} "
                    f"is already marked present today."
                )

            return jsonify({
                "success": True,
                "recognized": True,
                "student_id": result["student_id"],
                "name": result["name"],
                "message": message
            })

        return jsonify({
            "success": True,
            "recognized": False,
            "message": result["name"]
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        })


# -----------------------------------
# Attendance records
# -----------------------------------

@app.route("/attendance")
def attendance():

    records = get_attendance()

    data = []

    for record in records:

        data.append({
            "student_id": record["student_id"],
            "name": record["name"],
            "date": record["date"],
            "time": record["time"],
            "status": record["status"]
        })

    return jsonify(data)


# -----------------------------------
# Students
# -----------------------------------

@app.route("/students")
def students():

    records = get_students()

    data = []

    for student in records:

        data.append({
            "id": student["id"],
            "name": student["name"]
        })

    return jsonify(data)


# -----------------------------------
# Export CSV
# -----------------------------------

@app.route("/export")
def export():

    records = get_attendance()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Student ID",
        "Name",
        "Date",
        "Time",
        "Status"
    ])

    for record in records:

        writer.writerow([
            record["student_id"],
            record["name"],
            record["date"],
            record["time"],
            record["status"]
        ])

    response = Response(
        output.getvalue(),
        mimetype="text/csv"
    )

    response.headers[
        "Content-Disposition"
    ] = "attachment; filename=attendance_report.csv"

    return response


# -----------------------------------
# Run server
# -----------------------------------

if __name__ == "__main__":

    app.run(
    debug=True,
    host="0.0.0.0",
    port=5000
)