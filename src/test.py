import requests


def call_api(user_lat, user_lng, sw_lat, sw_lng, ne_lat, ne_lng):
    base_url = "http://127.0.0.1:5000"
    url = f"{base_url}?user_lat={user_lat}&user_lng={user_lng}&sw_lat={sw_lat}&sw_lng={sw_lng}&ne_lat={ne_lat}&ne_lng={ne_lng}"

    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': 'Failed to fetch data', 'status_code': response.status_code}
    
    
    
if __name__ == "__main__":
    bottom_left = (40.691726421417506, -73.99606021822756)
    top_right = (40.699674676429424, -73.9776159339345)
    userCoordinates = (40.693196621262665, -73.98783122985066)
    
    call_api(bottom_left[0], bottom_left[1], top_right[0], top_right[1], userCoordinates[0], userCoordinates[1])