from flask import Flask, render_template, request, jsonify
from flask_pymongo import PyMongo
import geocoder  # To get location (latitude/longitude)

app = Flask(__name__)
app.config.from_pyfile('config.py')

mongo = PyMongo(app)

# Serve Admin Page
@app.route('/')
def admin():
    return render_template('track_bus.html')

# Start Tracking - Store bus location in MongoDB
@app.route('/track_bus/<int:bus_id>', methods=['POST'])
def track_bus(bus_id):
    g = geocoder.ip('me')  # Get current location (lat, lng)
    
    if not g.latlng:
        return jsonify({"message": "Could not retrieve location"}), 500
    
    latitude, longitude = g.latlng
    location = g.city  # Approximate city name

    tracking_data = {
        "bus_id": bus_id,
        "latitude": latitude,
        "longitude": longitude,
        "location": location
    }

    mongo.db.track_bus.update_one(
        {"bus_id": bus_id},
        {"$set": tracking_data},
        upsert=True
    )

    return jsonify({"message": f"Tracking started for Bus ID {bus_id}."})

# Stop Tracking - Remove bus tracking from MongoDB
@app.route('/stop_tracking/<int:bus_id>', methods=['POST'])
def stop_tracking(bus_id):
    result = mongo.db.track_bus.delete_one({"bus_id": bus_id})

    if result.deleted_count > 0:
        return jsonify({"message": f"Tracking stopped for Bus ID {bus_id}."})
    else:
        return jsonify({"message": f"Bus ID {bus_id} not found in tracking."}), 404

if __name__ == '__main__':
    app.run(debug=True)
