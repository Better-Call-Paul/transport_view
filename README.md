# Subway-Surgers


## Functionality

Who are We?  
     Subway-Surger is an application that manages transportation pricing and congestion in New York City. We aim to provide users with tools to plan their commute efficiently while also reducing congestion on public transportation lines.Our platform empowers users to plan their commute efficiently while also providing valuable insights for individuals involved in the real estate market.

## Codebase
__Technologies__:
- Google Maps API integration
- HTML, CSS, and JavaScript
- CSP Library
- Flask
- Python


### Predictive Model Snippet:

```python
def predict_ridership(station_complex_id, day_of_week, hour):
    # Format the input features as a DataFrame
    input_features = pd.DataFrame({
        'station_complex_id': [station_complex_id],
        'day_of_week': [day_of_week],
        'hour': [hour]
    })
    # Predict ridership
    predicted_ridership = model.predict(input_features)
    return predicted_ridership[0]

    




