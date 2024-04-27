import pandas as pd
import json
from pymongo import MongoClient
import certifi

def load_and_convert_to_dataframe(filepath):
    """Load JSON data and convert it to a pandas DataFrame."""
    with open(filepath, 'r') as file:
        data = json.load(file)
    
    # Convert data to DataFrame
    stations = []
    for key, value in data.items():
        # Round the coordinates to four decimal places
        latitude = round(value['location'][0], 4)
        longitude = round(value['location'][1], 4)
        station_name = value['name']
        station = {
            'station_id': key,
            'name': station_name,
            'latitude': latitude,
            'longitude': longitude
        }
        stations.append(station)
    
    return pd.DataFrame(stations)

def load_json_to_dataframe(filepath):
    """Load a JSON file into a pandas DataFrame."""
    try:
        # Attempt to read the file directly with the default settings
        df = pd.read_json(filepath, lines=True)  # Use lines=True if each object is on a new line
    except ValueError as e:
        print(f"Error reading JSON: {e}")
        # Implement additional handling if the default read does not work
        with open(filepath, 'r') as file:
            data = json.load(file)  # This assumes the entire file is a single JSON array
        
        # Create DataFrame from list of dictionaries
        df = pd.DataFrame(data)
    
    return df


def join_dataframes(df1, df2):
    """Join two dataframes based on latitude and longitude."""
    # Ensure both DataFrames round latitude and longitude to the same number of decimal places
    df1['latitude'] = df1['latitude'].round(4)
    df1['longitude'] = df1['longitude'].round(4)
    df2['latitude'] = df2['latitude'].round(4)
    df2['longitude'] = df2['longitude'].round(4)
    
    # Merge on latitude and longitude
    merged_df = pd.merge(df1, df2, on=['latitude', 'longitude'], how='inner')
    return merged_df

def dataframe_to_dict(df):
    """Convert DataFrame to a list of dictionaries for MongoDB insertion."""
    return df.to_dict(orient='records')

def insert_data_into_mongodb(data):
    """Insert data into a MongoDB collection."""
    uri = 'mongodb+srv://ip2294:vZGaG2ngwrXFxZnL@mtastationdata.jwckd6t.mongodb.net/MTA?retryWrites=true&w=majority&appName=MTAStationData'
    client = MongoClient(uri, tlsCAFile=certifi.where())
    db = client['MTA']
    collection = db['ridership']    
    collection.insert_many(data)
    print("Data inserted into MongoDB successfully!")


def test_mongo_connection():
    uri = 'mongodb+srv://ip2294:vZGaG2ngwrXFxZnL@mtastationdata.jwckd6t.mongodb.net/MTA?retryWrites=true&w=majority&appName=MTAStationData'
    client = MongoClient(uri, tlsCAFile=certifi.where())
    db = client['MTA']
    collection = db['ridership']
    collection.insert_one({"_id":1, "user_name":"Bob"})
    print(collection.find())

# test_mongo_connection()

stations_df = load_and_convert_to_dataframe('stations.json')

# Join the dataframes

other_df = load_json_to_dataframe("HistoricalRidership.json")
result_df = join_dataframes(stations_df, other_df)
# print
data_to_insert = dataframe_to_dict(result_df)
# print(data_to_insert)

insert_data_into_mongodb(data_to_insert)

