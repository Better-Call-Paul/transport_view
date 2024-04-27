from dynamicPrice import getTicketPrice
from pymongo import MongoClient
import certifi
import json
from geopy.distance import geodesic

uri = 'mongodb+srv://ip2294:vZGaG2ngwrXFxZnL@mtastationdata.jwckd6t.mongodb.net/MTA?retryWrites=true&w=majority&appName=MTAStationData'
client = MongoClient(uri, tlsCAFile=certifi.where())
db = client['MTA']
collection = db['ridership']


def stationPrices(user_lat,user_lng,sw_lat , sw_lng , ne_lat , ne_lng):
    user_location = (user_lat, user_lng)
    stations = findStationsWithinViewport(sw_lat, sw_lng, ne_lat, ne_lng)
    priced_stations = getTicketPriceForAllStations(stations, user_location)
    return jsonify(priced_stations)


def findStationsWithinViewport(sw_lat, sw_lng, ne_lat, ne_lng):
    """Query the database for unique stations within a geographic rectangle."""
    query = [
        {
            '$match': {
                'latitude': {'$gte': sw_lat, '$lte': ne_lat},
                'longitude': {'$gte': sw_lng, '$lte': ne_lng}
            }
        },
        {
            '$group': {
                '_id': '$station_id',
                'name': {'$first': '$name'},
                'latitude': {'$first': '$latitude'},
                'longitude': {'$first': '$longitude'}
            }
        }
    ]
    stations_cursor = collection.aggregate(query)
    return list(stations_cursor)


def getTicketPriceForAllStations(stations, user_location):
    """Get dynamic ticket prices for a list of stations and sort them by distance."""
    for station in stations:
        station_id = station['_id']
        ticket_price = getTicketPrice(station_id)  # Assuming this function fetches real-time and historical congestion
        station['ticket_price'] = ticket_price
        # Calculate distance using coordinates reversed for geopy compatibility
        coordinates = (station['latitude'],station['longitude'])
        station['distance'] = calculateDistanceToUser(coordinates, user_location)
        station['coordinates'] = coordinates

    return sorted(stations, key=lambda x: x['distance'])

def calculateDistanceToUser(station_coords, user_coords):
    """Calculate the geographic distance between a station and the user's location."""
    return geodesic(station_coords[::-1], user_coords).miles


bottom_left = (40.686958996645735, -73.99845089784078)
top_right = (40.69811400013321, -73.96821435817587)
user_location = (40.693196621262665, -73.98783122985066)


stations = findStationsWithinViewport(bottom_left[0], bottom_left[1], top_right[0], top_right[1])
print(stations)
priced_stations = getTicketPriceForAllStations(stations, user_location)
print(json.dumps(priced_stations, indent=4)) 
# print("Sorted Stations with Pricing Info:")
# for station in priced_stations:
#     print(station)