from flask import Flask, request, jsonify
from retrival import stationPrices


app = Flask(__name__)

@app.route('/stations', methods=['GET'])
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
    return jsonify(localStationPrices)


if __name__ == '__main__':
    app.run(debug=True)

