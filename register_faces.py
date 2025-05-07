import face_recognition
import cv2
import pickle
import os

def register_faces(name):
    video_capture = cv2.VideoCapture(0)

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
            continue  # Continue the loop if no face is detected

        if len(face_encodings) > 1:
            print("[ERROR] Multiple faces detected. Please ensure only one face is visible.")
            continue  # Continue the loop if multiple faces are detected

        # If only one face is detected, save the encoding
        print("[INFO] Face detected. Registering...")

        # Load existing encodings if they exist
        if os.path.exists("encodings.pickle"):
            with open("encodings.pickle", "rb") as f:
                existing_data = pickle.load(f)
            existing_encodings = existing_data["encodings"]
            existing_names = existing_data["names"]
        else:
            existing_encodings = []
            existing_names = []

        # Append the new face encoding and name
        existing_encodings.append(face_encodings[0])
        existing_names.append(name)

        # Save updated data
        data = {"encodings": existing_encodings, "names": existing_names}
        with open("encodings.pickle", "wb") as f:
            pickle.dump(data, f)

        print(f"[INFO] Face registered for {name}")
        video_capture.release()

        return f"{name} Face registered successfully!"
