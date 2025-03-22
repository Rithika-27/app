from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_pymongo import PyMongo
import bcrypt

app = Flask(__name__)

app.config.from_pyfile('config.py')

mongo = PyMongo(app)

# Home Page
@app.route('/')
def index():
    return render_template('index.html')


# Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        email = request.form['email']

        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

        # Check if email already exists
        if mongo.db.users.find_one({"email": email}):
            return jsonify(success=False, message="Email already registered.")

        try:
            mongo.db.users.insert_one({
                "username": username,
                "password": hashed_password,
                "email": email
            })
            session['logged_in'] = True
            session['email'] = email
            session.modified = True  # Ensure session updates

            return jsonify(success=True)
        
        except Exception as e:
            print(f"Error occurred: {e}")
            return jsonify(success=False, message="Registration failed. Please try again.")
    
    return render_template('register.html')


# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        user = mongo.db.users.find_one({"email": email})

        if user and bcrypt.checkpw(password, user['password'].encode('utf-8')):  # Ensure bytes conversion
            session['logged_in'] = True
            session['email'] = email
            session.modified = True  # Ensure session updates
            return redirect(url_for('mapping'))

        return render_template('login.html', error="Invalid email or password.")
    
    return render_template('login.html')


# Enable Location Page
@app.route('/mapping', methods=['GET', 'POST'])
def mapping():
    if session.get('logged_in'):
        if request.method == 'POST' and 'enable_location' in request.form:
            return render_template('location.html')
        return render_template('mapping.html')
    return redirect(url_for('login'))


# Actual Location Page
@app.route('/location')
def location():
    return render_template('location.html')


# Start and End Location Page
@app.route('/combine', methods=['GET', 'POST'])
def combine():
    return render_template('combine.html')


# Fetch Bus Routes
@app.route('/bus_routes', methods=['GET'])
def bus_routes():
    start_location = request.args.get('startLocation')
    end_location = request.args.get('endLocation')

    if not start_location or not end_location:
        return render_template('bus_routes.html', bus_routes=[], error="Please provide both start and end locations.")

    try:
        bus_routes = list(mongo.db.bus_routes.find(
            {"start_location": start_location, "end_location": end_location},
            {"_id": 0}
        ))

        if not bus_routes:
            return render_template('bus_routes.html', bus_routes=[], error="No routes found.")

        return render_template('bus_routes.html', bus_routes=bus_routes)
    
    except Exception as e:
        print(f"DEBUG: Error retrieving bus routes - {e}")
        return render_template('bus_routes.html', bus_routes=[], error=f"Error retrieving data: {str(e)}")


# Fetch Bus Timings
@app.route('/bus_timing/<bus_id>', methods=['GET'])
def bus_timing(bus_id):
    try:
        try:
            bus_id = int(bus_id)
        except ValueError:
            return render_template('bus_timing.html', bus_timings=[], error="Invalid Bus ID format.")

        bus_timings = list(mongo.db.bus_timing.find({"bus_id": bus_id}))
        
        if not bus_timings:
            return render_template('bus_timing.html', bus_timings=[], error="No timings found for this bus.")

        formatted_timings = [
            {
                "id": str(timing["_id"]), 
                "bus_id": timing["bus_id"],
                "timing": timing.get("time", "N/A")  # Avoid missing time key
            }
            for timing in bus_timings
        ]

        return render_template('bus_timing.html', bus_timings=formatted_timings)

    except Exception as e:
        import traceback
        print(traceback.format_exc()) 

        return render_template('bus_timing.html', bus_timings=[], error=f"Error retrieving data: {str(e)}")


@app.route('/get_bus_location/<bus_id>', methods=['GET'])
def get_bus_location(bus_id):
    bus_data = mongo.db.track_bus.find_one({"bus_id": bus_id}, {"_id": 0})  # Exclude MongoDB's default _id field

    if not bus_data:
        return jsonify({"error": "No location found for this Bus ID"}), 404

    return render_template("track_bus.html", bus_data=bus_data)

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
