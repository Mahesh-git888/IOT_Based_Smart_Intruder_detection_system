import face_recognition
import cv2
import pickle
import numpy as np
from datetime import datetime
import shutil
import os

# # Define the face distance threshold (you can tweak this value based on your needs)
# FACE_DISTANCE_THRESHOLD = 0.6  # Lower values mean stricter matching

# def predict_faces():
#     # Load encodings
#     with open("encodings.pickle", "rb") as f:
#         data = pickle.load(f)

#     video_capture = cv2.VideoCapture(0)

#     print("[INFO] Starting face recognition. Press 'q' to quit.")

#     while True:
#         ret, frame = video_capture.read()
#         if not ret:
#             break

#         # Resize for faster performance
#         small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
#         rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

#         # Detect faces and encode
#         face_locations = face_recognition.face_locations(rgb_small_frame)
#         face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             matches = face_recognition.compare_faces(data["encodings"], face_encoding)
#             name = "Unknown"

#             face_distances = face_recognition.face_distance(data["encodings"], face_encoding)
            
#             # Find the best match
#             if len(face_distances) > 0:
#                 best_match_index = np.argmin(face_distances)
#                 if face_distances[best_match_index] < FACE_DISTANCE_THRESHOLD:  # Only recognize if the distance is below the threshold
#                     if matches[best_match_index]:
#                         name = data["names"][best_match_index]

#             # Scale back face coordinates to original image size
#             top *= 4
#             right *= 4
#             bottom *= 4
#             left *= 4

#             # Draw the rectangle around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

#             # Display the name of the person
#             cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

#             # Get current timestamp for saving image
#             now = datetime.now()
#             folder_path = f"database/{now.month}/{now.day}/{now.hour}"
#             os.makedirs(folder_path, exist_ok=True)

#             # Construct the image path
#             if name == "Unknown":
#                 image_path = os.path.join(folder_path, f"Unknown_{now.minute}.jpg")
#                 label = "Intruder"
#             else:
#                 image_path = os.path.join(folder_path, f"{name}_{now.minute}.jpg")
#                 label = "Safe"

#             # Save the image with the bounding box and name
#             cv2.imwrite(image_path, frame)
#             print(f"[INFO] Image saved as {image_path}")

#             # Prepare response based on recognition
#             response = {"name": name, "label": label}
#             print(f"[INFO] Response: {response}")

#             # You can return or send the response in your desired format (e.g., via API, logging, etc.)

#         # Show the resulting frame with the bounding box
#         cv2.imshow("Face Recognition", frame)

#         # Exit when 'q' is pressed
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     # Release video capture and close OpenCV windows
#     video_capture.release()
#     cv2.destroyAllWindows()
    


def predict_faces():
    url = "http://100.67.60.205:8080/video"
    # Load encodings
    with open("encodings.pickle", "rb") as f:
        data = pickle.load(f)

    video_capture = cv2.VideoCapture(url)
    # video_capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    print("[INFO] Starting face recognition. Press 'q' to quit.")

    recognized_name = None
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        # Resize for faster performance
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Detect faces and encode
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(data["encodings"], face_encoding)
            name = "Unknown"

            face_distances = face_recognition.face_distance(data["encodings"], face_encoding)

            # Find the best match
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if face_distances[best_match_index] < 0.6:  # Only recognize if the distance is below the threshold
                    if matches[best_match_index]:
                        name = data["names"][best_match_index]

            # Scale back face coordinates to original image size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw the rectangle around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            # Display the name of the person
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

            # Get current timestamp for saving image
            now = datetime.now()
            folder_path = f"database/{now.month}/{now.day}/{now.hour}"
            os.makedirs(folder_path, exist_ok=True)

            # Construct the image path
            if name == "Unknown":
                image_path = os.path.join(folder_path, f"Unknown_{now.minute}.jpg")
                label = "Intruder"
            else:
                image_path = os.path.join(folder_path, f"{name}_{now.minute}.jpg")
                label = "Safe"

            # Save the image with the bounding box and name
            cv2.imwrite(image_path, frame)
            print(f"[INFO] Image saved as {image_path}")
            
        
# After saving the original image_path
            frontend_path = os.path.join("static/captured", os.path.basename(image_path))
            shutil.copy(image_path, frontend_path)

            return name, os.path.basename(frontend_path)


        # Show the resulting frame with the bounding box
        cv2.imshow("Face Recognition", frame)

        # Exit when 'q' is pressed (to terminate the video capture after face is recognized)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release video capture and close OpenCV windows
    video_capture.release()
    cv2.destroyAllWindows()

    return recognized_name