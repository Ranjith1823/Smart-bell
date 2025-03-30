import json
import os
import io
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

# Correctly load Firebase credentials
cred = credentials.Certificate(json.loads(firebase_credentials_json))
firebase_admin.initialize_app(cred, {"databaseURL": FIREBASE_DB_URL})

# Load Firebase Web API Key from environment variables
FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY")
if not FIREBASE_WEB_API_KEY:
    raise ValueError("Firebase Web API Key is missing in environment variables!")


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
