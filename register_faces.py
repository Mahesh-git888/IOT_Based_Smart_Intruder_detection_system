import face_recognition
import cv2
from db_helper import DatabaseHelper

def register_faces(name):
    video_capture = cv2.VideoCapture(0)
    db_helper = DatabaseHelper()

    print("[INFO] Capturing image. Please look at the camera...")

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("[ERROR] Failed to capture image.")
            return "Failed to capture image."

        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect faces and encode
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        if len(face_encodings) == 0:
            print("[ERROR] No face detected. Please look at the camera.")
            continue

        if len(face_encodings) > 1:
            print("[ERROR] Multiple faces detected. Please ensure only one face is visible.")
            continue

        # Save face encoding to MongoDB
        db_helper.save_face_encoding(face_encodings[0], name)
        print(f"[INFO] Face registered for {name}")
        video_capture.release()

        return f"{name} Face registered successfully!"
