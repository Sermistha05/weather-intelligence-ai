def evaluate_alerts(
    wind_speed: float,
    humidity: float,
    temp: float,
    predicted_temp: float,
    rain_probability_pct: float,
) -> list[dict]:
    alerts = []

    if rain_probability_pct >= 70:
        alerts.append({
            "type": "high_rain_probability",
            "severity": "high",
            "title": "High Rain Probability",
            "message": f"Rain probability is {rain_probability_pct}%. Carry an umbrella and avoid low-lying areas.",
        })
    elif rain_probability_pct >= 50:
        alerts.append({
            "type": "moderate_rain_probability",
            "severity": "moderate",
            "title": "Moderate Rain Probability",
            "message": f"Rain probability is {rain_probability_pct}%. Consider carrying an umbrella.",
        })

    if wind_speed >= 40:
        alerts.append({
            "type": "high_wind",
            "severity": "high",
            "title": "High Wind Speed",
            "message": f"Wind speed is {wind_speed} km/h. Secure loose objects and avoid exposed areas.",
        })

    if humidity >= 85:
        alerts.append({
            "type": "very_high_humidity",
            "severity": "moderate",
            "title": "Very High Humidity",
            "message": f"Humidity is {humidity}%. Expect discomfort outdoors; stay hydrated.",
        })

    if abs(predicted_temp - temp) >= 3:
        direction = "rise" if predicted_temp > temp else "drop"
        alerts.append({
            "type": "temperature_change",
            "severity": "moderate",
            "title": "Notable Temperature Change Expected",
            "message": f"Temperature may {direction} from {temp}°C to {predicted_temp}°C. Dress in layers.",
        })

    return alerts
