from flask import Flask, request, jsonify
from joblib import load
import pandas as pd

app = Flask(__name__)

# Load the model
model = load('models/fiveMillionDatapointModel.joblib')

@app.route('/predict', methods=['POST'])
def predict():
    # Get JSON request
    print("success")
    data = request.get_json(force=True)
    print(data)
    
    # Convert JSON data to DataFrame
    input_data = pd.DataFrame([data])
    
    # Predict
    prediction = model.predict(input_data)
    
    # Return prediction
    return jsonify(prediction.tolist())

if __name__ == '__main__':
    app.run(debug=True,port=8080)
