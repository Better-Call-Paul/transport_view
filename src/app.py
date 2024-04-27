from flask import Flask, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
import random
import threading
import time
import csp 
from csp import ts 
import requests 

app = Flask(__name__)
CORS(app)  # Enable CORS on all routes


stations = {}
def update_station_prices(sw_lat, sw_lng, ne_lat, ne_lng, user_lat, user_lng):
    # Enter the application context
    with app.app_context():
        base_url = "http://127.0.0.1:5000"
        url = f"{base_url}?user_lat={user_lat}&user_lng={user_lng}&sw_lat={sw_lat}&sw_lng={sw_lng}&ne_lat={ne_lat}&ne_lng={ne_lng}"
        
        # Construct the query parameters with provided coordinates
        params = {
            'user_lat': user_lat,
            'user_lng': user_lng,
            'sw_lat': sw_lat,
            'sw_lng': sw_lng,
            'ne_lat': ne_lat,
            'ne_lng': ne_lng
        }

        try:
            response = requests.get(url)
            if response.status_code == 200:
                response_data = response.json()
                for station_data in response_data:
                    name = station_data["name"]
                    if name not in stations:
                        stations[name] = {
                            'neighborhood': station_data['neighborhood'],
                            'lat': station_data['latitude'],
                            'lon': station_data['longitude'],
                            'price': station_data['ticket_price'],
                            'distance': station_data['distance']
                        }
                    else:
                        # Directly update the price with the latest value from the API
                        stations[name]['price'] = station_data['ticket_price']
            else:
                print(f"Failed to fetch data, Status Code: {response.status_code}")
        except Exception as e:
            print(f"Exception occurred: {e}")
def periodically_update_prices(interval, sw_lat, sw_lng, ne_lat, ne_lng, user_lat, user_lng):
    while True:
        update_station_prices(sw_lat, sw_lng, ne_lat, ne_lng, user_lat, user_lng)
        time.sleep(interval)  # Sleep for the defined interval in seconds
    

def fluctuate_prices():
    # update this with api calls
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
    # Coordinates
    bottom_left = (40.691726421417506, -73.99606021822756)
    top_right = (40.699674676429424, -73.9776159339345)
    userCoordinates = (40.693196621262665, -73.98783122985066)

    # Create the thread with correct argument passing
    price_update_thread = threading.Thread(target=periodically_update_prices, args=(5, bottom_left[0], bottom_left[1], top_right[0], top_right[1], userCoordinates[0], userCoordinates[1]))
    price_update_thread.daemon = True
    price_update_thread.start()
    
    app.run(debug=True, port=8000)
