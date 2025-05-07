from flask import Flask, render_template, send_from_directory, request, jsonify
import os
from dotenv import load_dotenv
import threading

# Local fucntions import
from predict_face import predict_faces 
from register_faces import register_faces

app = Flask(__name__) 


load_dotenv()
url = os.getenv("URL")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/captured/<path:filename>')
def serve_image(filename):
    return send_from_directory('static/captured', filename)

@app.route('/api/register_face', methods=['GET'])
def register():
    # Get the 'name' from the query parameters
    name = request.args.get('name')
    
    if name:
        register_faces(name)
        return jsonify({"status": "success", "message": f"Face registered for {name}"})
    else:
        return jsonify({"status": "error", "message": "Name parameter is missing"})



# @app.route('/api/predict_face', methods=['POST'])
# def predict():
#     # Start the face recognition in a separate thread so the API call is non-blocking
#     def recognition_thread():
#         global recognized_name
#         recognized_name = predict_faces()
    
#     # Start the thread
#     thread = threading.Thread(target=recognition_thread)
#     thread.start()
#     thread.join()  # Ensure that the main thread waits for the recognition thread to finish
    
#     # Return the result to the client
#     if recognized_name:
#         return jsonify({"status": "success", "recognized": recognized_name})
#     else:
#         return jsonify({"status": "error", "message": "No face detected or recognized."})

@app.route('/api/predict_face', methods=['POST'])
def predict():
    name, image_name = predict_faces()
    label = "safe" if name != "Unknown" else "Intruder"
    return jsonify({"name": name, "label": label, "image_path": image_name})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
    
