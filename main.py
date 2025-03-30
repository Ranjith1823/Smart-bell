from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db, auth
import os
import json

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load Firebase credentials from environment variable
firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")
if firebase_credentials:
    cred_dict = json.loads(firebase_credentials)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': "https://smart-bell-7b0c3-default-rtdb.asia-southeast1.firebasedatabase.app/"
    })
else:
    raise ValueError("FIREBASE_CREDENTIALS environment variable not set")

# Function to verify Firebase user authentication
def verify_token(token):
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        return None

# Function to get holidays (Everyone can access)
def get_holidays():
    ref = db.reference("holidays")
    return ref.get() or {}

# Function to add a holiday (Only authenticated users)
def add_holiday(date, description):
    ref = db.reference("holidays")
    ref.child(date).set({"description": description})

# Function to remove a holiday (Only authenticated users)
def remove_holiday(date):
    ref = db.reference("holidays")
    if ref.child(date).get():
        ref.child(date).delete()
        return True
    return False

# Serve Frontend
@app.route('/')
def index():
    return render_template("index.html")

# ✅ Fetch Holidays (Everyone can access)
@app.route('/get_holidays', methods=['GET'])
def fetch_holidays():
    holidays = get_holidays()
    return jsonify(holidays)

# ✅ User Login (Verify Firebase Token)
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    token = data.get("token")
    user = verify_token(token)
    
    if user:
        return jsonify({"status": "success", "message": "Login successful", "user": user})
    return jsonify({"status": "error", "message": "Invalid token"}), 401

# ✅ Add Holiday (Authenticated Users Only)
@app.route('/add_holiday', methods=['POST'])
def add_holiday_route():
    data = request.json
    token = data.get("token")
    user = verify_token(token)

    if not user:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
    date = data.get("date")
    description = data.get("description")
    if not date or not description:
        return jsonify({"status": "error", "message": "Date and description required"}), 400
    
    add_holiday(date, description)
    return jsonify({"status": "success", "message": "Holiday added"})

# ✅ Remove Holiday (Authenticated Users Only)
@app.route('/remove_holiday', methods=['POST'])
def remove_holiday_route():
    data = request.json
    token = data.get("token")
    user = verify_token(token)

    if not user:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    date = data.get("date")
    if remove_holiday(date):
        return jsonify({"status": "success", "message": "Holiday removed"})
    
    return jsonify({"status": "error", "message": "Holiday not found"}), 404

# ✅ User Logout (Handled on Frontend)
@app.route('/logout', methods=['POST'])
def logout():
    return jsonify({"status": "success", "message": "User logged out"})

# Run Flask App
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
