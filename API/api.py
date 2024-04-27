from flask import Flask, request, jsonify
from dynamicPrice import getTicketPrice
from pymongo import MongoClient
import certifi
from geopy.distance import geodesic
from retrival import stationPrices


# app = Flask(__name__)

uri = 'mongodb+srv://ip2294:vZGaG2ngwrXFxZnL@mtastationdata.jwckd6t.mongodb.net/MTA?retryWrites=true&w=majority&appName=MTAStationData'
client = MongoClient(uri, tlsCAFile=certifi.where())
db = client['MTA']
collection = db['ridership']

# @app.route('/stations', methods=['GET'])
def getLocalStationPrices():
    user_lat = request.args.get('user_lat', type=float)
    user_lng = request.args.get('user_lng', type=float)
    sw_lat = request.args.get('sw_lat', type=float)
    sw_lng = request.args.get('sw_lng', type=float)
    ne_lat = request.args.get('ne_lat', type=float)
    ne_lng = request.args.get('ne_lng', type=float)

    if not (user_lat and user_lng and sw_lat and sw_lng and ne_lat and ne_lng):
        return jsonify({'error': 'Missing required parameters'}), 400

    localStationPrices = stationPrices(user_lat,user_lng,sw_lat , sw_lng , ne_lat , ne_lng)
    user_location = (user_lat, user_lng)
    stations = findStationsWithinViewport(sw_lat, sw_lng, ne_lat, ne_lng)
    priced_stations = getTicketPriceForAllStations(stations, user_location)
    return jsonify(priced_stations)

def findStationsWithinViewport(sw_lat, sw_lng, ne_lat, ne_lng):
    """Query the database for stations within a geographic rectangle defined by the viewport."""
    query = {
        'georeference': {
            '$geoWithin': {
                '$box': [
                    [sw_lng, sw_lat],
                    [ne_lng, ne_lat]
                ]
            }
        }
    }
    # Project only the necessary fields
    stations_cursor = collection.find(query, {'_id': 0, 'station_id': 1, 'name': 1, 'georeference.coordinates': 1})
    return list(stations_cursor)

def getTicketPriceForAllStations(stations, user_location):
    """Get dynamic ticket prices for a list of stations and sort them by distance."""
    for station in stations:
        station_id = station['station_id']
        ticket_price = getTicketPrice(station_id)  # Assuming this function fetches real-time and historical congestion
        station['ticket_price'] = ticket_price
        # Calculate distance using coordinates reversed for geopy compatibility
        station['distance'] = calculateDistanceToUser(station['georeference']['coordinates'], user_location)
        station['coordinates'] = station['georeference']['coordinates']
        del station['georeference']  # Remove the georeference key

    return sorted(stations, key=lambda x: x['distance'])

def calculateDistanceToUser(station_coords, user_coords):
    """Calculate the geographic distance between a station and the user's location."""
    return geodesic(station_coords[::-1], user_coords).miles


bottom_left = (40.691726421417506, -73.99606021822756)
top_right = (40.699674676429424, -73.9776159339345)
user_location = (40.693196621262665, -73.98783122985066)


stations = findStationsWithinViewport(bottom_left[0], bottom_left[1], top_right[0], top_right[1])
priced_stations = getTicketPriceForAllStations(stations, user_location)
print(jsonify(priced_stations)) 
print("Sorted Stations with Pricing Info:")
for station in priced_stations:
    print(station)
# if __name__ == '__main__':
#     app.run(debug=True)


# @app.route('/stations',methods=['GET'])
# def getLocalStationPrices():
#     user_lat = request.args.get('user_lat', type=float)
#     user_lng = request.args.get('user_lng', type=float)
#     sw_lat = request.args.get('sw_lat', type=float)
#     sw_lng = request.args.get('sw_lng', type=float)
#     ne_lat = request.args.get('ne_lat', type=float)
#     ne_lng = request.args.get('ne_lng', type=float)
#     user_location = [user_lat,user_lng]
#     stations = findStationsWithinViewport(sw_lat,sw_lng,ne_lat,ne_lng,user_location)
#     return "sorted list/json/data structure in terms of distance to the user's location, of the station name, its coordinates, dynamic price"
    
#     # current location of user
#     # Get viewpoint coordinates
#         # Find all the stations within the viewpoint coordinates that the user is in
#         # get the price for them
#         # return sorted list/json/data structure in terms of distance to the user's location, of the station name, its coordinates, dynamic price


# bottom_left = 40.691726421417506, -73.99606021822756
# top_right = 40.699674676429424, -73.9776159339345
# userCoordinates = 40.693196621262665, -73.98783122985066