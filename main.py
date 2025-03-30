# from flask import Flask, render_template, request, jsonify
# from flask_cors import CORS
# import firebase_admin
# from firebase_admin import credentials, db
# import os
# import json

# # Initialize Flask app
# app = Flask(__name__)
# CORS(app)

# # Load Firebase credentials from environment variable
# firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")
# if firebase_credentials:
#     cred_dict = json.loads(firebase_credentials)
#     cred = credentials.Certificate(cred_dict)
#     firebase_admin.initialize_app(cred, {
#         'databaseURL': "https://smart-bell-7b0c3-default-rtdb.asia-southeast1.firebasedatabase.app/"
#     })
# else:
#     raise ValueError("FIREBASE_CREDENTIALS environment variable not set")

# # Function to get holidays
# def get_holidays():
#     ref = db.reference("holidays")
#     return ref.get() or {}

# # Function to add a holiday
# def add_holiday(date, description):
#     ref = db.reference("holidays")
#     ref.child(date).set({"description": description})

# # Function to remove a holiday
# def remove_holiday(date):
#     ref = db.reference("holidays")
#     if ref.child(date).get():
#         ref.child(date).delete()
#         return True
#     return False

# # Serve Frontend
# @app.route('/')
# def index():
#     return render_template("index.html")

# # Fetch Holidays
# @app.route('/get_holidays', methods=['GET'])
# def fetch_holidays():
#     holidays = get_holidays()
#     return jsonify(holidays)

# # Add Holiday
# @app.route('/add_holiday', methods=['POST'])
# def add_holiday_route():
#     data = request.json
#     date = data.get("date")
#     description = data.get("description")
#     if not date or not description:
#         return jsonify({"status": "error", "message": "Date and description required"}), 400
#     add_holiday(date, description)
#     return jsonify({"status": "success", "message": "Holiday added"})

# # Remove Holiday
# @app.route('/remove_holiday', methods=['POST'])
# def remove_holiday_route():
#     data = request.json
#     date = data.get("date")
#     if remove_holiday(date):
#         return jsonify({"status": "success", "message": "Holiday removed"})
#     return jsonify({"status": "error", "message": "Holiday not found"}), 404

# # Run Flask App
# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=5000, debug=True)


import json
import os
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

FIREBASE_DB_URL = "https://smart-bell-7b0c3-default-rtdb.asia-southeast1.firebasedatabase.app/"

# Load Firebase credentials from environment variables
firebase_credentials_json = os.getenv("FIREBASE_CREDENTIALS")

if not firebase_credentials_json:
    raise ValueError("Firebase credentials not found in environment variables!")

cred = credentials.Certificate(json.loads(firebase_credentials_json))
firebase_admin.initialize_app(cred, {"databaseURL": FIREBASE_DB_URL})


# Serve Frontend (Ensure index.html is in the templates folder)
@app.route("/")
def home():
    return render_template("index.html")


# Login using Firebase REST API for email/password sign-in
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"status": "error", "message": "Email and password are required"}), 400

    FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY")
    if not FIREBASE_WEB_API_KEY:
        return jsonify({"status": "error", "message": "Firebase Web API Key is missing"}), 500

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    response_data = response.json()

    if response.status_code == 200:
        return jsonify({"status": "success", "data": response_data})
    else:
        error_message = response_data.get("error", {}).get("message", "Login failed")
        return jsonify({"status": "error", "message": error_message}), 401


# Get all holidays from Firebase Realtime Database
@app.route("/get_holidays", methods=["GET"])
def get_holidays():
    ref = db.reference("holidays")
    holidays = ref.get() or {}
    print("DEBUG: Holidays from Firebase:", holidays)
    return jsonify(holidays)


# Add a holiday (date should be unique)
@app.route("/add_holiday", methods=["POST"])
def add_holiday():
    data = request.json
    date = data.get("date")
    description = data.get("description")

    if not date or not description:
        return jsonify({"status": "error", "message": "Date and description are required"}), 400

    ref = db.reference("holidays")
    ref.child(date).set({"description": description})
    print("DEBUG: Added holiday:", {date: {"description": description}})
    return jsonify({"status": "success", "message": "Holiday added successfully!"})


# Remove a holiday by date
@app.route("/remove_holiday", methods=["POST"])
def remove_holiday():
    data = request.json
    date = data.get("date")

    if not date:
        return jsonify({"status": "error", "message": "Date is required"}), 400

    ref = db.reference("holidays")
    if not ref.child(date).get():
        return jsonify({"status": "error", "message": "Holiday not found"}), 404

    ref.child(date).delete()
    print("DEBUG: Removed holiday for date:", date)
    return jsonify({"status": "success", "message": "Holiday removed successfully!"})


if __name__ == "__main__":
    app.run(debug=True)
