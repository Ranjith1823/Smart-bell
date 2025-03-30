from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Firebase Initialization
cred = credentials.Certificate("D:/git/Smart-bell/firebase_credentials.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://smart-bell-7b0c3-default-rtdb.asia-southeast1.firebasedatabase.app/"
})

# Function to get holidays
def get_holidays():
    ref = db.reference("holidays")
    return ref.get() or {}

# Function to add a holiday
def add_holiday(date, description):
    ref = db.reference("holidays")
    ref.child(date).set({"description": description})

# Function to remove a holiday
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

# Fetch Holidays
@app.route('/get_holidays', methods=['GET'])
def fetch_holidays():
    holidays = get_holidays()
    return jsonify(holidays)

# Add Holiday
@app.route('/add_holiday', methods=['POST'])
def add_holiday_route():
    data = request.json
    date = data.get("date")
    description = data.get("description")

    if not date or not description:
        return jsonify({"status": "error", "message": "Date and description required"}), 400

    add_holiday(date, description)
    return jsonify({"status": "success", "message": "Holiday added"})

# Remove Holiday
@app.route('/remove_holiday', methods=['POST'])
def remove_holiday_route():
    data = request.json
    date = data.get("date")

    if remove_holiday(date):
        return jsonify({"status": "success", "message": "Holiday removed"})
    return jsonify({"status": "error", "message": "Holiday not found"}), 404

# Run Flask App
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
