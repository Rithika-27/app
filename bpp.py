from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_pymongo import PyMongo
from datetime import datetime
from config import MONGO_URI  # Ensure your config file has the MongoDB URI

app = Flask(__name__)
app.config["MONGO_URI"] = MONGO_URI
mongo = PyMongo(app)



# Serve Admin Page
@app.route('/')
def admin():
    return render_template('track_bus.html')

@app.route('/store_location', methods=['POST'])
def store_location():
    data = request.json
    bus_id = data.get("bus_id")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    location = data.get("location")

    if not bus_id or not latitude or not longitude or not location:
        return jsonify({"message": "Missing data"}), 400

    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')  # UTC timestamp

    mongo.db.track_bus.update_one(
        {"bus_id": bus_id},
        {"$set": {
            "latitude": latitude,
            "longitude": longitude,
            "location": location,
            "timestamp": timestamp
        }},
        upsert=True
    )

    return jsonify({"message": f"Location updated for Bus ID {bus_id} at {timestamp}."})

if __name__ == '__main__':
    app.run(debug=True)
















