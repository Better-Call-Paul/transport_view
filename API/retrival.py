from dynamicPrice import getTicketPrice
from pymongo import MongoClient
import certifi
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from geopy.distance import geodesic


uri = 'mongodb+srv://ip2294:vZGaG2ngwrXFxZnL@mtastationdata.jwckd6t.mongodb.net/MTA?retryWrites=true&w=majority&appName=MTAStationData'
client = MongoClient(uri, tlsCAFile=certifi.where())
db = client['MTA']
collection = db['ridership']

def load_neighborhoods(filepath):
    with open(filepath, 'r') as file:
        data = json.load(file)
    neighborhoods = {}
    for name, coords in data.items():
        # Split and convert coordinates to floats; assume format "lng, lat, lng, lat"
        sw_lng, sw_lat, ne_lng, ne_lat = map(float, coords.split(", "))
        neighborhoods[name] = [(sw_lng, sw_lat), (ne_lng, ne_lat)]
    return neighborhoods

neighborhoods = load_neighborhoods('resources/neighborhoods.json')

def assign_neighborhood(latitude, longitude, neighborhoods):
    for neighborhood, ((sw_lng, sw_lat), (ne_lng, ne_lat)) in neighborhoods.items():
        if (sw_lng <= longitude <= ne_lng) and (sw_lat <= latitude <= ne_lat):
            return neighborhood
    return "NA"  # Default to "NA" if no neighborhood is found


def stationPrices(user_lat,user_lng,sw_lat , sw_lng , ne_lat , ne_lng):
    user_location = (user_lat, user_lng)
    stations = findStationsWithinViewport(sw_lat, sw_lng, ne_lat, ne_lng,neighborhoods)
    priced_stations = getTicketPriceForAllStations(stations, user_location)
    return json.dumps(priced_stations)


def findStationsWithinViewport(sw_lat, sw_lng, ne_lat, ne_lng, neighborhoods):
    """Query the database for unique stations within a geographic rectangle."""
    query = [
    {
        '$match': {
            'latitude': {'$gte': min(sw_lat, ne_lat), '$lte': max(sw_lat, ne_lat)},
            'longitude': {'$gte': min(sw_lng, ne_lng), '$lte': max(sw_lng, ne_lng)}
        }
    },
    {
        '$group': {
            '_id': '$name',  # Group by station name
            'firstRecord': {'$first': '$$ROOT'}  # Keep the first document encountered for each group
        }
    },
    {
        '$replaceRoot': {'newRoot': '$firstRecord'}  # Replace the document in the result set with the first record
    },
    {
        '$project': {
            '_id': 0,  # Exclude the default MongoDB _id field from the final output
            'station_id': 1,
            'name': 1,
            'latitude': 1,
            'longitude': 1,
            'ticket_price': 1,  # Ensure to include any other fields you may need in the output
            'distance': 1,
            'coordinates': 1
        }
    }
]
    stations_cursor = collection.aggregate(query)
    stations = list(stations_cursor)
    for station in stations:
        neighborhood = assign_neighborhood(station['latitude'], station['longitude'], neighborhoods)
        station['neighborhood'] = neighborhood
    return stations

def getTicketPriceForStation(station, user_location):
    try:
        station_id = station['station_id']
        ticket_price = getTicketPrice(station_id)
        coordinates = (station['latitude'], station['longitude'])
        distance = calculateDistanceToUser(coordinates, user_location)
        station['ticket_price'] = ticket_price
        station['distance'] = distance
        station['coordinates'] = coordinates
    except KeyError as e:
        print(f"KeyError: {e} - Check station fields: {station}")
    return station

def getTicketPriceForAllStations(stations, user_location):
    processed_stations = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(getTicketPriceForStation, station, user_location) for station in stations]
        for future in as_completed(futures):
            processed_stations.append(future.result())
    return sorted(processed_stations, key=lambda x: x['distance'])

# def getTicketPriceForAllStations(stations, user_location):
#     for station in stations:
#         print(station)  # Debugging: See what each station object contains
#         station_id = station['station_id']
#         ticket_price = getTicketPrice(station_id)
#         station['ticket_price'] = ticket_price
#         try:
#             coordinates = (station['latitude'], station['longitude'])
#             station['distance'] = calculateDistanceToUser(coordinates, user_location)
#             station['coordinates'] = coordinates
#         except KeyError as e:
#             print(f"KeyError: {e} - Check station fields: {station}")

#     with ThreadPoolExecutor(max_workers=10) as executor:
#         # Future object to station info mapping
#         future_to_station = {executor.submit(get_ticket_price_for_station, station, user_location): station for station in stations}
#         for future in concurrent.futures.as_completed(future_to_station):
#             station = future_to_station[future]
#             try:
#                 ticket_price, distance = future.result()
#                 station['ticket_price'] = ticket_price
#                 station['distance'] = distance
#             except Exception as exc:
#                 print(f'{station["station_id"]} generated an exception: {exc}')
#     return sorted(stations, key=lambda x: x['distance'])




def calculateDistanceToUser(station_coords, user_coords):
    """Calculate the geographic distance between a station and the user's location."""
    corrected_station_coords = (station_coords[1], station_coords[0])
    corrected_user_coords = (user_coords[1], user_coords[0])
    return geodesic(corrected_station_coords, corrected_user_coords).miles


# bottom_left = (40.686958996645735, -73.99845089784078)
# top_right = (40.69811400013321, -73.96821435817587)
# user_location = (40.693196621262665, -73.98783122985066)


# stations = findStationsWithinViewport(bottom_left[0], bottom_left[1], top_right[0], top_right[1])
# print(stations)
# priced_stations = getTicketPriceForAllStations(stations, user_location)
# print(json.dumps(priced_stations, indent=4)) 
# print("Sorted Stations with Pricing Info:")
# for station in priced_stations:
#     print(station)