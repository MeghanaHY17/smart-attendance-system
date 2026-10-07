import os
import cv2
import numpy as np
import face_recognition


def save_face(image_data, filename):

    os.makedirs("faces", exist_ok=True)

    image_array = np.frombuffer(
        image_data,
        np.uint8
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    if image is None:
        return False, "Invalid image."

    rgb_image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    face_locations = face_recognition.face_locations(
        rgb_image
    )

    if len(face_locations) == 0:
        return False, "No face detected."

    if len(face_locations) > 1:
        return False, "Please keep only one person in the camera."

    cv2.imwrite(
        filename,
        image
    )

    return True, "Face saved successfully."


def load_known_faces(students):

    known_faces = []
    known_ids = []
    known_names = []

    for student in students:

        face_file = student["face_file"]

        if not os.path.exists(face_file):
            continue

        image = face_recognition.load_image_file(
            face_file
        )

        encodings = face_recognition.face_encodings(
            image
        )

        if len(encodings) == 0:
            continue

        known_faces.append(
            encodings[0]
        )

        known_ids.append(
            student["id"]
        )

        known_names.append(
            student["name"]
        )

    return (
        known_faces,
        known_ids,
        known_names
    )


def recognize_face(image_data, students):

    image_array = np.frombuffer(
        image_data,
        np.uint8
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    if image is None:
        return {
            "recognized": False,
            "name": "Invalid image"
        }

    rgb_image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    locations = face_recognition.face_locations(
        rgb_image
    )

    encodings = face_recognition.face_encodings(
        rgb_image,
        locations
    )

    if len(encodings) == 0:
        return {
            "recognized": False,
            "name": "No face detected"
        }

    known_faces, known_ids, known_names = load_known_faces(
        students
    )

    if len(known_faces) == 0:
        return {
            "recognized": False,
            "name": "No registered faces"
        }

    face_encoding = encodings[0]

    distances = face_recognition.face_distance(
        known_faces,
        face_encoding
    )

    best_match = np.argmin(distances)

    tolerance = 0.50

    if distances[best_match] <= tolerance:

        return {
            "recognized": True,
            "student_id": known_ids[best_match],
            "name": known_names[best_match],
            "distance": float(distances[best_match])
        }

    return {
        "recognized": False,
        "name": "Unknown"
    }