from realTimeParse import getStationCongestion
from datetime import datetime
from pymongo import MongoClient
import certifi
import requests



uri = 'mongodb+srv://ip2294:vZGaG2ngwrXFxZnL@mtastationdata.jwckd6t.mongodb.net/MTA?retryWrites=true&w=majority&appName=MTAStationData'
client = MongoClient(uri, tlsCAFile=certifi.where())
db = client['MTA']
collection = db['ridership']

# Constants
BASE_TICKET_PRICE = 2.90
MAX_PRICE_FLUCTUATION = 0.50  # up to 50 cents fluctuation for minor adjustments
MAX_DECREASE = 0.50  # Maximum decrease in price
MIN_DECREASE = 0.10  # Minimum decrease in price


# Weights
WEIGHT_REAL_TIME = 0.3  # 20% weight for real-time congestion
WEIGHT_HISTORICAL = 0.7  # 80% weight for historical congestion


def calculateCombinedCongestion(realTimeScore, historicalScore=10.0):
    print("Real time score", realTimeScore)
    return (float(realTimeScore) * WEIGHT_REAL_TIME) + (float(historicalScore) * WEIGHT_HISTORICAL)

def getPriceAdjustment(combinedCongestion):
    # print(f"CombinedCongestion: {combinedCongestion}")
    if combinedCongestion >= 10:  # Hypothetical threshold for high congestion
        return MAX_PRICE_FLUCTUATION
    elif combinedCongestion >= 5:  # Moderate congestion
        return MAX_PRICE_FLUCTUATION * 0.5
    elif combinedCongestion <= 2:
        # print("returned this")
        return -MAX_DECREASE  # Maximum discount for very low congestion
    elif combinedCongestion < 5:
        return -MIN_DECREASE  # Some discount for moderate congestion
    else:
        return 0  # No discount for high congestion

def calculateDynamicPrice(congestionScore):
    """Calculate the dynamic price based on the congestion score."""
    adjustment = getPriceAdjustment(congestionScore)
    dynamicPrice = BASE_TICKET_PRICE + adjustment
    return round(dynamicPrice, 2)

def getHistoricalCongestion(stationId):
    now = datetime.now()
    dayOfWeek = now.weekday()
    hour = now.hour

    station_data = collection.find_one({'station_id': stationId})
    if not station_data:
        return None  # or handle the error as needed
    station_complex_id = station_data.get('station_complex_id')

    api_url = 'http://model-api-url.com/get_congestion'
    params = {'station_id': station_complex_id, 'day': dayOfWeek, 'hour': hour}
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        congestion_data = response.json()
        return congestion_data.get('ridership')
    else:
        return None  # or handle API error as needed

    # datetime to find current day of week 
    # also find the rounded down floor hour, 0-23
    # convert stationId to complexId from mongoDB
    # call Model API station, day of week(0 indexing), hour
    # return ridershare
    

def getTicketPrice(stationId):
    """Fetch the current congestion score and compute the dynamic ticket price."""
    stationCongestion = getStationCongestion(stationId)[1]
    # print(stationCongestion, type(stationCongestion))
    historicalCongestion = getHistoricalCongestion(stationId)
    congestionScore = calculateCombinedCongestion(stationCongestion)  # Assume this function fetches the current score
    return calculateDynamicPrice(congestionScore)


print(getTicketPrice("232"))