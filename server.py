import io
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flask_cors import CORS
import datetime
import os
from dotenv import load_dotenv
import smtplib

# Local functions import
from predict_face import predict_faces 
from register_faces import register_faces
from db_helper import DatabaseHelper

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "your_secret_key")  # Still keep secret key for other functionality

# Admin credentials
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "admin123"
}

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username == ADMIN_CREDENTIALS["username"] and password == ADMIN_CREDENTIALS["password"]:
        # Return a success response with the redirect URL to index.html
        return jsonify({
            "status": "success", 
            "message": "Login successful",
            "redirect": "/dashboard"  # This route serves index.html
        })
    return jsonify({"status": "error", "message": "Invalid username or password"}), 401

@app.route('/dashboard')
def dashboard():
    return render_template('index.html')  # This serves the main application page

# Main page route
@app.route('/')
def index():
    # Redirect to login route
    return redirect(url_for('login_page'))

# Login page route
@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/api/register_face', methods=['GET'])
def register():
    # Get the 'name' from the query parameters
    name = request.args.get('name')
    
    if name:
        register_faces(name)
        return jsonify({"status": "success", "message": f"Face registered for {name}"})
    else:
        return jsonify({"status": "error", "message": "Name parameter is missing"})
    
@app.route('/api/predict_face', methods=['POST'])
def predict():
    try:
        name, image_name = predict_faces()
        if image_name is None:
            return jsonify({
                "status": "error",
                "message": "Failed to capture image"
            }), 500
        label = "safe" if name != "Unknown" else "Intruder"
        return jsonify({
            "status": "success",
            "name": name,
            "label": label,
            "image_path": f"api/image/{image_name}"  # Update path to use MongoDB route
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/predict_face_simple', methods=['GET'])
def predict_face_simple():
    try:
        name, _ = predict_faces()
        # Return 1 if recognized (safe), 0 if unknown (unsafe)
        result = 1 if name != "Unknown" else 0
        return jsonify({
            "result": result,
            "name": name
        })
    except Exception as e:
        return jsonify({
            "result": -1,  # Error code
            "error": str(e)
        }), 500

@app.route('/api/image/<image_name>')
def get_image(image_name):
    db_helper = DatabaseHelper()
    image_data = db_helper.get_image(image_name)
    if image_data:
        return send_file(
            io.BytesIO(image_data),
            mimetype='image/jpeg'
        )
    return jsonify({"error": "Image not found"}), 404

@app.route('/api/clear_data', methods=['POST'])
def clear_data():
    try:
        db_helper = DatabaseHelper()
        db_helper.clear_all_data()
        return jsonify({"status": "success", "message": "All face data cleared successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/user_history/<name>', methods=['GET'])
def get_user_history(name):
    db_helper = DatabaseHelper()
    
    # Check if we're requesting all timestamps for dialog view
    full_timestamps = request.args.get('full', 'false').lower() == 'true'
    
    history = db_helper.get_user_history(name, full_timestamps)
    if history:
        # Convert timestamps to string format for JSON serialization
        history['timestamps'] = [ts.strftime('%Y-%m-%d %H:%M:%S') 
                               for ts in history['timestamps']]
        return jsonify({
            'status': 'success',
            'data': history
        })
    return jsonify({
        'status': 'error',
        'message': 'User not found'
    }), 404

def serialize_timestamp(ts):
    if isinstance(ts, datetime.datetime): 
        return ts.isoformat()
    return ts


@app.route('/api/all_users', methods=['GET'])
def get_all_users():
    try:
        db_helper = DatabaseHelper()
        users_data = db_helper.get_all_users()

        formatted_users = []
        for user in users_data or []:
            formatted_users.append({
                'name': user.get('name', 'N/A'),
                'visit_count': user.get('visit_count', 0),
                'timestamps': [serialize_timestamp(ts) for ts in user.get('timestamps', [])],
                'images': [
                    {
                        'image_name': img.get('image_name'),
                        'image_data': img.get('image_data'),
                        'timestamp': serialize_timestamp(img.get('timestamp'))
                    }
                    for img in user.get('images', [])
                ]
            })

        return jsonify({
            'status': 'success',
            'data': formatted_users
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/all_users')
def redirect_all_users():
    """Redirect the /all_users endpoint to the correct API endpoint /api/all_users"""
    return redirect(url_for('get_all_users'))

@app.route('/api/open_gate', methods=['POST'])
def open_gate():
    return jsonify({
            "status": "success",
            "name": 'Onwer',
            "label": 'safe',
        })
    
@app.route('/api/logout', methods=['POST'])
def logout():
    response = jsonify({"status": "success", "message": "Logged out successfully"})
    # No need to clear JWT token cookie as it's not being used
    return response

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)