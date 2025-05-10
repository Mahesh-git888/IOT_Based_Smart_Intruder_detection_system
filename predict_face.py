# import face_recognition
# import cv2
# import numpy as np
# from datetime import datetime
# import os
# from db_helper import DatabaseHelper
# from sms import send_alert_sms

# def predict_faces():
#     # url = "http://192.168.168.80:8080/video"
#     url = 0
#     db_helper = DatabaseHelper()
    
#     # Get encodings from MongoDB
#     data = db_helper.get_all_encodings()
#     if not data['encodings']:
#         print("[ERROR] No face encodings found. Please register faces first.")
#         video_capture = cv2.VideoCapture(url)
#         ret, frame = video_capture.read()
#         if ret:
#             image_name = db_helper.save_image(frame, "Unknown")
#             video_capture.release()
#             # Send SMS alert for unknown person
#             send_alert_sms()
#             return "Unknown", image_name
#         video_capture.release()
#         return "Unknown", None

#     video_capture = cv2.VideoCapture(url)


#     print("[INFO] Starting face recognition. Press 'q' to quit.")

#     recognized_name = None
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
#                 if face_distances[best_match_index] < 0.45:  # Only recognize if the distance is below the threshold
#                     if matches[best_match_index]:
#                         name = data["names"][best_match_index]

#             # Scale back face coordinates to original image size
#             top *= 4
#             right *= 4
#             bottom *= 4
#             left *= 4

#             # Draw the rectangle around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
#             cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

#             # Save image using database helper only
#             image_name = db_helper.save_image(frame, name)
#             print(f"[INFO] Image saved to database")
            
#             # If the face is unknown, send an SMS alert
#             if name == "Unknown":
#                 print("[ALERT] Unknown person detected! Sending SMS alert...")
#                 send_alert_sms()

#             return name, image_name

#         # Show the resulting frame with the bounding box
#         cv2.imshow("Face Recognition", frame)

#         # Exit when 'q' is pressed (to terminate the video capture after face is recognized)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     # Release video capture and close OpenCV windows
#     video_capture.release()
#     cv2.destroyAllWindows()

#     return recognized_name


import face_recognition
import cv2
import numpy as np
from datetime import datetime
from db_helper import DatabaseHelper
from sms import send_alert_sms

def predict_faces(url):
    db_helper = DatabaseHelper()

    # Get stored encodings
    data = db_helper.get_all_encodings()
    if not data['encodings']:
        print("[ERROR] No registered encodings. Please register faces first.")
        video_capture = cv2.VideoCapture(url)
        ret, frame = video_capture.read()
        if ret:
            image_name = db_helper.save_image(frame, "Unknown")
            video_capture.release()
            send_alert_sms()
            return "Unknown", image_name
        video_capture.release()
        return "Unknown", None

    video_capture = cv2.VideoCapture(url)
    print("[INFO] Starting fast face recognition...")

    recognized_name = None
    frame_skip = 0  # Optional: skip every other frame for speed

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        if frame_skip % 2 == 0:
            small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")  # "cnn" if GPU
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                face_distances = face_recognition.face_distance(data["encodings"], face_encoding)
                name = "Unknown"

                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if face_distances[best_match_index] < 0.5:
                        name = data["names"][best_match_index]

                # Scale coordinates back
                top *= 2
                right *= 2
                bottom *= 2
                left *= 2

                # Draw box and label
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

                image_name = db_helper.save_image(frame, name)
                print(f"[INFO] Saved image: {image_name}")

                if name == "Unknown":
                    print("[ALERT] Unknown detected! Sending SMS...")
                    send_alert_sms()

                # Early exit after one recognition
                video_capture.release()
                cv2.destroyAllWindows()
                return name, image_name

        frame_skip += 1
        cv2.imshow("Fast Face Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    return recognized_name
