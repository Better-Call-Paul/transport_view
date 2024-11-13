import time
import os 
import threading
from datetime import datetime, timedelta

import nyct_gtfs 
from nyct_gtfs import NYCTFeed

import csp
from csp.impl.pushadapter import PushInputAdapter
from csp.impl.wiring import py_push_adapter_def


class Event(csp.Struct):
    train: nyct_gtfs.trip.Trip
    update: nyct_gtfs.stop_time_update.StopTimeUpdate
    arrival: datetime
    direction: str

# Create a runtime implementation of the adapter
class FetchTrainDataAdapter(PushInputAdapter):
    def __init__(self, interval, stations):
        self._interval = interval
        self._thread = None
        self._running = False
        self._stations = stations

    def start(self, starttime, endtime):
        print("FetchTrainDataAdapter::start")
        self._running = True
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def stop(self):
        print("FetchTrainDataAdapter::stop")
        if self._running:
            self._running = False
            self._thread.join()

    def _run(self):
        # This is where we will read and process the real-time data feed
        feed = nyct_gtfs.NYCTFeed("https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs", api_key="")

        while self._running:
            print("----------------------------------------------")
            print(f"{datetime.utcnow()}: refreshing MTA feed")
            print("----------------------------------------------")
            print("                                     Station     | Line | Direction   | Arrival time")
            feed.refresh()
            trains = feed.filter_trips(underway=True, headed_for_stop_id=self._stations)
            # tick whenever feed is refreshed
            for train in trains:
                for update in train.stop_time_updates:
                    if update.stop_id in self._stations:
                        self.push_tick(Event(train=train, update=update, direction=train.direction, arrival=update.arrival))
            time.sleep(self._interval.total_seconds())




def main():
    
    feed = NYCTFeed("https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs", api_key="")
    feed.refresh()
    
    trains = feed.filter_trips()
    """
    feed.filter_trips(
    line_id=None,
    travel_direction=None,
    train_assigned=None,
    underway=None,
    shape_id=None,
    headed_for_stop_id=None,
    updated_after=None,
    has_delay_alert=None,
    )
    """
    
    for train in trains:
        print(train)
        
    
    trains_at_penn = []
    print("Station | Line | Direction | Arrival time")
    for train in trains:
        for update in train.stop_time_updates:
            if update.stop_id in ['128S', '128N']:
                print(f"{update.stop_name} | {train.route_id} | {train.headsign_text} | {update.arrival}")
                trains_at_penn.append((train, update))
                
    # Create the graph-time representation of our adapter
    FetchTrainData = py_push_adapter_def("FetchTrainData", FetchTrainDataAdapter, csp.ts[Event], interval=timedelta, stations=list)

    @csp.node
    def pretty_print(train_data: csp.ts[Event], count: csp.ts[float]) -> csp.ts[str]:
        message = f" {train_data.update.stop_name} |   {train_data.train.route_id}  | {train_data.train.headsign_text} | {train_data.update.arrival} | Southbound train count: {int(count)}"
        return message

    @csp.graph
    def mta_graph():
        print("Start of graph building")
        stations = ['128S', '128N']
        interval = timedelta(seconds=30)
        trains_at_penn = FetchTrainData(interval, stations=stations)
        # trains_at_penn is an edge that can be processed through a node.
        # Select all southbound trains going through Penn Station
        south_trains = csp.filter(trains_at_penn.direction == "S", trains_at_penn)
        # Convert timestamps to unique float values
        timestamp = csp.apply(south_trains.arrival, datetime.timestamp, float)
        # Count the number of unique entries in this timeseries block (reset every 30 seconds)
        count = csp.stats.count(csp.stats.unique(timestamp), interval=timedelta(seconds=30), min_window=timedelta(seconds=1))
        result = pretty_print(trains_at_penn, count)
        csp.print(":", result)
        print("End of graph building")

    start = datetime.utcnow()
    end = start + timedelta(minutes=3)
    csp.run(mta_graph, starttime=start, realtime=True, endtime=end)
    print("Done.")
            
    


if __name__ == "__main__":
    main()