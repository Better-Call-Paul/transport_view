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
    print("FOUND PRICED STATIONS")
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
        station['ticket_price'] = ticket_price if ticket_price is not None else "N/A"
        station['distance'] = distance if distance is not None else float('inf')
        station['coordinates'] = coordinates
    except KeyError as e:
        print(f"KeyError: {e} - Check station fields: {station}")
        station['ticket_price'] = "Error"
        station['distance'] = float('inf')  # Set a default large value to indicate error
        station['coordinates'] = (0, 0)  # Default coordinates
    except Exception as e:
        print(f"General error processing station {station.get('station_id', 'Unknown')}: {e}")
        station['ticket_price'] = "Error"
        station['distance'] = float('inf')  # Set a default large value to indicate error
        station['coordinates'] = (0, 0)  # Default coordinates
    return station



def getTicketPriceForAllStations(stations, user_location):
    processed_stations = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(getTicketPriceForStation, station, user_location): station for station in stations}
        for future in as_completed(futures):
            try:
                result = future.result()
                if 'distance' in result:  # Ensure distance is present
                    processed_stations.append(result)
                else:
                    print(f"Missing 'distance' in station data: {result}")
            except Exception as e:
                station = futures[future]
                print(f"Failed to process station {station.get('station_id', 'Unknown')}: {e}")
    # Proceed to sort only if 'distance' is present
    return sorted(processed_stations, key=lambda x: x.get('distance', float('inf')))



def calculateDistanceToUser(station_coords, user_coords):
    """Calculate the geographic distance between a station and the user's location."""
    corrected_station_coords = (station_coords[1], station_coords[0])
    corrected_user_coords = (user_coords[1], user_coords[0])
    return geodesic(corrected_station_coords, corrected_user_coords).miles
