
import face_recognition
import cv2
from db_helper import DatabaseHelper
import numpy as np

def register_faces(name):
    video_capture = cv2.VideoCapture(0)
    db_helper = DatabaseHelper()

    print("[INFO] Capturing image. Please look at the camera...")

    encodings_list = []
    max_attempts = 20
    confidence_threshold = 0.4  # Lower = more confident

    attempts = 0

    while attempts < max_attempts:
        ret, frame = video_capture.read()
        if not ret:
            print("[ERROR] Failed to capture image.")
            video_capture.release()
            return "Failed to capture image."

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        if len(face_encodings) == 0:
            print("[ERROR] No face detected. Please look at the camera.")
            attempts += 1
            continue

        if len(face_encodings) > 1:
            print("[ERROR] Multiple faces detected. Please ensure only one face is visible.")
            attempts += 1
            continue

        # Save the encoding for evaluation
        encodings_list.append(face_encodings[0])
        print(f"[INFO] Captured frame {len(encodings_list)} with a face")

        if len(encodings_list) >= 5:
            # Calculate pairwise distances
            distances = []
            for i in range(len(encodings_list)):
                for j in range(i + 1, len(encodings_list)):
                    dist = np.linalg.norm(encodings_list[i] - encodings_list[j])
                    distances.append(dist)

            avg_distance = np.mean(distances)
            print(f"[DEBUG] Average consistency distance: {avg_distance:.4f}")

            if avg_distance < confidence_threshold:
                final_encoding = np.mean(encodings_list, axis=0)
                db_helper.save_face_encoding(final_encoding, name)
                print(f"[INFO] Face registered for {name}")
                video_capture.release()
                return f"{name} Face registered successfully!"
            else:
                print("[WARNING] Face not stable/confident enough. Please try again with better lighting.")
                video_capture.release()
                return "Face not stable enough. Please try again with better lighting and keep your face steady."

        attempts += 1

    video_capture.release()
    return "Face registration failed. Please try again under proper lighting conditions with only one visible face."
