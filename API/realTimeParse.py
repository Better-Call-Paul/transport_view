import requests
import gtfs_realtime_pb2
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


def fetchTrainData(endpoint):
    """Fetch train data from the GTFS Realtime endpoint."""
    response = requests.get(endpoint)
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)
    return feed

def findTrainsAndDelaysAtStation(feed, stationId):
    """Extract trains and their delays at a specific station from the GTFS feed."""
    trains = []
    delays = []
    for entity in feed.entity:
        if entity.HasField('trip_update'):
            for stopUpdate in entity.trip_update.stop_time_update:
                if stopUpdate.stop_id.startswith(stationId):
                    if stopUpdate.arrival.time:
                        arrivalTime = datetime.datetime.fromtimestamp(stopUpdate.arrival.time)
                        trains.append(arrivalTime)
                    if stopUpdate.arrival.delay:
                        delays.append(stopUpdate.arrival.delay)  # Delay in seconds
    return trains, delays

def calculateFrequency(trains):
    """Calculate the frequency of trains based on their arrival times."""
    if len(trains) < 2:
        return None
    trains.sort()
    intervals = [t2 - t1 for t1, t2 in zip(trains, trains[1:])]
    averageInterval = sum(intervals, datetime.timedelta()) / len(intervals)
    return averageInterval

def calculateDelayImpact(delays):
    """Calculate a delay impact score based on the average delay."""
    if not delays:
        return 0
    averageDelay = sum(delays) / len(delays)
    if averageDelay > 300:  # Delays over 5 minutes
        return 10
    elif averageDelay > 60:  # Delays over 1 minute
        return 5
    return 0

def calculateCongestion(frequency, delayImpact):
    """Calculate the congestion score based on train frequency and delay impact."""
    score = 0
    if frequency:
        minutes = frequency.total_seconds() / 60
        score += max(0, 10 - minutes)  # Less frequent trains increase congestion score
    score += delayImpact  # Add the impact of delays in minutes
    return round(score, 2)

def getStationCongestion(stationId):
    """Main function to determine congestion score for a station."""
    startTime = datetime.datetime.now()
    endpoints = [
    'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace',
    'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm',
    'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g',
    'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz',
    'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw',
    'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l',
    'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs',
    'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-si'
    ]
    allTrains = []
    allDelays = []
    with ThreadPoolExecutor(max_workers=len(endpoints)) as executor:
        future_to_endpoint = {executor.submit(fetchTrainData, endpoint): endpoint for endpoint in endpoints}
        
        for future in as_completed(future_to_endpoint):
            endpoint = future_to_endpoint[future]
            try:
                feed = future.result()
                trains, delays = findTrainsAndDelaysAtStation(feed, stationId)
                allTrains.extend(trains)
                allDelays.extend(delays)
            except Exception as exc:
                print(f'{endpoint} generated an exception: {exc}')

    frequency = calculateFrequency(allTrains)
    delayImpact = calculateDelayImpact(allDelays)
    congestionScore = calculateCongestion(frequency, delayImpact)
    endTime = datetime.datetime.now()
    elapsedTime = endTime - startTime

    if frequency:
        # print(f"Average interval between trains at station {stationId}: {frequency}")
        # print(f'Average delay impact is {delayImpact}')
        # print(f"Congestion Score: {congestionScore}")
        # print(f"With a time of {elapsedTime} seconds.")
        return frequency, congestionScore
    else:
        print(f"No data available to calculate frequency for station {stationId}")
        return 0.0,0.0

