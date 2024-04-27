from pymongo import MongoClient
import certifi
import requests

uri = 'mongodb+srv://ip2294:vZGaG2ngwrXFxZnL@mtastationdata.jwckd6t.mongodb.net/MTA?retryWrites=true&w=majority&appName=MTAStationData'
client = MongoClient(uri, tlsCAFile=certifi.where())
db = client['MTA']
collection = db['ridership']

station_data = collection.find_one({'station_id': "232"})
print(station_data)

api_url = 'http://127.0.0.1:8080/predict'
params = {'station_complex_id': 283, 'day_of_week': 6, 'hour': 3}

data = {
    'station_complex_id': 283,
    'day_of_week': 6,
    'hour': 3
}
response = requests.post(api_url, json=data)
print(response)