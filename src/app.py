from flask import Flask, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
import random
import threading
import time

app = Flask(__name__)
CORS(app)  # Enable CORS on all routes


client = MongoClient("mongodb+srv://ip2294:vZGaG2ngwrXFxZnL@mtastationdata.jwckd6t.mongodb.net/?retryWrites=true&w=majority&appName=MTAStationData")
db = client["MTA"]
collection = db["ridership"]


stations = {
    "Grand Central 1": {"neighborhood": "Manhattan", "lat": 40.7527, "lon": -73.9772, "price": random.uniform(2.5, 5)},
    "Times Square 1": {"neighborhood": "Manhattan", "lat": 40.7553, "lon": -73.9869, "price": random.uniform(2.5, 5)},
    "Grand Central 2": {"neighborhood": "Alphabet City", "lat": 40.7258, "lon": -73.9775, "price": random.uniform(2.5, 5)},
    "Times Square 2": {"neighborhood": "Bronx", "lat": 40.8161, "lon": -73.8964, "price": random.uniform(2.5, 5)},
    "Grand Central 3": {"neighborhood": "Bronx", "lat": 40.7527, "lon": -73.9772, "price": random.uniform(2.5, 5)},
}

    # "Station Name": {"neighborhood": "Neighborhood", "lat": latitude, "lon": longitude, "price": random_price()}


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

@app.route('/api/average-prices')
def api_average_prices():
    # Calculate average prices per neighborhood
    neighborhood_prices = {}
    for station in stations.values():
        neighborhood = station['neighborhood']
        if neighborhood not in neighborhood_prices:
            neighborhood_prices[neighborhood] = []
        neighborhood_prices[neighborhood].append(station['price'])
    averages = {
        neighborhood: round(sum(prices) / len(prices), 2)
        for neighborhood, prices in neighborhood_prices.items()
    }
    return jsonify(averages)

if __name__ == '__main__':

    thread = threading.Thread(target=fluctuate_prices)
    thread.daemon = True
    thread.start()
    app.run(debug=True)