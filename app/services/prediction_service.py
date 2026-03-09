import joblib
import pandas as pd

# load trained model
model = joblib.load("temperature_model.pkl")

def predict_temperature(humidity, pressure, wind_speed, hour):
    data = pd.DataFrame({
        "hour": [hour],
        "humidity": [humidity],
        "pressure": [pressure],
        "wind_speed": [wind_speed]
    })

    prediction = model.predict(data)

    return round(float(prediction[0]), 1)