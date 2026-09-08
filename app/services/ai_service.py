from google import genai
from app.core.config import settings


def _fallback_insight(city, temp, humidity, wind_speed, predicted_temp, rain_pct, will_rain):
    trend = "rise" if predicted_temp > temp + 0.5 else ("drop" if predicted_temp < temp - 0.5 else "remain steady")
    rain_level = "high" if rain_pct >= 60 else ("moderate" if rain_pct >= 30 else "low")
    rain_advice = "Carry an umbrella if heading out." if will_rain else "Conditions look mostly dry."
    hydration = " Stay hydrated in the heat." if temp >= 32 else ""
    return (
        f"{city} is currently {temp}°C with {humidity}% humidity and winds at {wind_speed} km/h. "
        f"Temperature is expected to {trend} to {predicted_temp}°C. "
        f"Rain risk is {rain_level} at {rain_pct}%. "
        f"{rain_advice}{hydration}"
    )


def generate_insight(
    city: str,
    temp: float,
    humidity: float,
    pressure: float,
    wind_speed: float,
    rain: int,
    predicted_temp: float,
    rain_probability_pct: float,
    will_rain: bool,
) -> str:
    if not settings.GEMINI_API_KEY:
        return _fallback_insight(city, temp, humidity, wind_speed, predicted_temp, rain_probability_pct, will_rain)

    prompt = f"""City: {city}

Current weather:
Temperature: {temp}°C
Humidity: {humidity}%
Pressure: {pressure} hPa
Wind speed: {wind_speed} km/h
Current rain: {"Yes" if rain else "No"}

ML predictions:
Predicted temperature: {predicted_temp}°C
Rain probability: {rain_probability_pct}%
Rain prediction: {"Rain expected" if will_rain else "No rain expected"}

Generate a concise weather intelligence insight covering:
1. Current weather summary
2. Temperature trend interpretation (compare current {temp}°C to predicted {predicted_temp}°C)
3. Rain-risk interpretation using the supplied {rain_probability_pct}% probability
4. One practical recommendation

Rules:
- Be clear and conversational.
- Do not invent weather measurements.
- Do not claim certainty about future weather.
- Explicitly distinguish current observed weather from ML prediction.
- Use the supplied ML probability rather than inventing a different one.
- Do not mention that you are an AI.
- Return plain text only. No markdown headings. No JSON."""

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config={"max_output_tokens": 350},
        )
        return response.text.strip()
    except Exception:
        return _fallback_insight(city, temp, humidity, wind_speed, predicted_temp, rain_probability_pct, will_rain)
