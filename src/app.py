from flask import Flask, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
import random
import threading
import time

app = Flask(__name__)
CORS(app)  # Enable CORS on all routes

# Connect to MongoDB (replace with your connection details)
client = MongoClient("mongodb+srv://ip2294:vZGaG2ngwrXFxZnL@mtastationdata.jwckd6t.mongodb.net/?retryWrites=true&w=majority&appName=MTAStationData")
db = client["MTA"]
collection = db["ridership"]


stations = {
    "Grand Central": {"lat": 40.7527, "lon": -73.9772, "price": random.uniform(2.5, 5)},
    "Times Square": {"lat": 40.7553, "lon": -73.9869, "price": random.uniform(2.5, 5)}
    # Add more stations as needed
}

# Function to fluctuate prices every 3 seconds
def fluctuate_prices():
    while True:
        for station in stations.values():
            station['price'] = round(random.uniform(2.5, 5), 2)
        time.sleep(3)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stations')
def api_stations():
    return jsonify([{**station_info, 'name': name} for name, station_info in stations.items()])

# Start the background thread for fluctuating prices
fluctuation_thread = threading.Thread(target=fluctuate_prices)
fluctuation_thread.daemon = True
fluctuation_thread.start()

if __name__ == '__main__':
    app.run(debug=True)