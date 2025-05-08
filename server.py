import io
from flask import Flask, render_template, request, jsonify, send_file, redirect
from flask_cors import CORS
import jwt
import datetime
import os
from dotenv import load_dotenv
from functools import wraps
import smtplib

# Local functions import
from predict_face import predict_faces 
from register_faces import register_faces
from db_helper import DatabaseHelper




# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "your_secret_key")  # Replace with a strong secret key


# Admin credentials
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "admin123"
}

# JWT token validation decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('jwtToken')  # Retrieve the token from cookies
        if not token:
            return jsonify({"status": "error", "message": "Token is missing"}), 403
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"status": "error", "message": "Token has expired"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"status": "error", "message": "Invalid token"}), 403
        return f(*args, **kwargs)
    return decorated

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username == ADMIN_CREDENTIALS["username"] and password == ADMIN_CREDENTIALS["password"]:
        token = jwt.encode(
            {"username": username, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
            app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        response = jsonify({"status": "success", "message": "Login successful"})
        response.set_cookie('jwtToken', token, httponly=True)  # Set the token as an HTTP-only cookie
        return response
    return jsonify({"status": "error", "message": "Invalid username or password"}), 401
# Main page route
@app.route('/')
def index():
    token = request.cookies.get('jwtToken')  # Retrieve the token from cookies
    if not token:
        return redirect('/login')  # Redirect to login page if no token is found
    try:
        jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        return render_template('index.html')  # Render the main page if the token is valid
    except jwt.ExpiredSignatureError:
        return redirect('/login')  # Redirect to login if the token has expired
    except jwt.InvalidTokenError:
        return redirect('/login')  # Redirect to login if the token is invalid

# Login page route
@app.route('/login')
def login_page():
    return render_template('login.html')

# Example protected API route
@app.route('/api/protected', methods=['GET'])
@token_required
def protected():
    return jsonify({"status": "success", "message": "You have access to this protected route!"})


@app.route('/api/register_face', methods=['GET'])
@token_required
def register():
    # Get the 'name' from the query parameters
    name = request.args.get('name')
    
    if name:
        register_faces(name)
        return jsonify({"status": "success", "message": f"Face registered for {name}"})
    else:
        return jsonify({"status": "error", "message": "Name parameter is missing"})
    
    
@app.route('/api/predict_face', methods=['POST'])
@token_required
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

# Add this route to serve images directly from MongoDB if needed
@app.route('/api/image/<image_name>')
@token_required
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
@token_required
def clear_data():
    try:
        db_helper = DatabaseHelper()
        db_helper.clear_all_data()
        return jsonify({"status": "success", "message": "All face data cleared successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/user_history/<name>', methods=['GET'])
@token_required
def get_user_history(name):
    db_helper = DatabaseHelper()
    history = db_helper.get_user_history(name)
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
    
## For opening the gate
@app.route('/api/open_gate', methods=['POST']) 
@token_required
def open_gate():
    return jsonify({
            "status": "success",
            "name": 'Onwer',
            "label": 'safe',
        })
    
@app.route('/api/logout', methods=['POST'])
def logout():
    response = jsonify({"status": "success", "message": "Logged out successfully"})
    response.set_cookie('jwtToken', '', expires=0)  # Clear the JWT token cookie
    return response

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

