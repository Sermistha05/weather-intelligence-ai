import json
from google import genai
from app.core.config import settings


def _fallback_insight(city, temp, humidity, wind_speed, predicted_temp, rain_pct, will_rain) -> dict:
    trend = "rise" if predicted_temp > temp + 0.5 else ("drop" if predicted_temp < temp - 0.5 else "remain steady")
    rain_level = "high" if rain_pct >= 60 else ("moderate" if rain_pct >= 30 else "low")
    hydration = " Stay hydrated in the heat." if temp >= 32 else ""
    return {
        "summary": f"{city} is currently {temp}°C with {humidity}% humidity and winds at {wind_speed} km/h.{hydration}",
        "clothing": "Light, breathable clothing recommended." if temp >= 28 else ("Warm layers advised." if temp < 15 else "Comfortable casual clothing is suitable."),
        "rain_advice": f"Rain risk is {rain_level} at {rain_pct}%. Carry an umbrella if heading out." if will_rain else f"Rain risk is {rain_level} at {rain_pct}%. Conditions look mostly dry.",
        "outdoor_activity": "Outdoor activities are not recommended due to rain risk." if will_rain else "Conditions are suitable for outdoor activities.",
        "advisory": f"Temperature is expected to {trend} to {predicted_temp}°C. Plan accordingly.",
    }


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
) -> dict:
    if not settings.GEMINI_API_KEY:
        return _fallback_insight(city, temp, humidity, wind_speed, predicted_temp, rain_probability_pct, will_rain)

    city = city[:100]
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

You are a weather advisor. Return ONLY a valid JSON object with exactly these five keys:
- "summary": one sentence current weather overview
- "clothing": one sentence clothing recommendation based on temperature and rain
- "rain_advice": one sentence rain risk interpretation using the supplied {rain_probability_pct}% probability
- "outdoor_activity": one sentence outdoor activity recommendation
- "advisory": one sentence temperature trend note comparing current {temp}°C to predicted {predicted_temp}°C

Rules:
- Be clear and conversational.
- Do not invent weather measurements.
- Do not claim certainty about future weather.
- Explicitly distinguish current observed weather from ML prediction.
- Use the supplied ML probability rather than inventing a different one.
- Do not mention that you are an AI.
- Return valid JSON only. No markdown. No code fences. No extra text."""

    try:
        client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
            http_options=genai.types.HttpOptions(timeout=30000),
        )
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                max_output_tokens=350,
                temperature=0.7,
            ),
        )
        raw = response.text.strip()
        # Strip markdown code fences if model wraps response despite instructions
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        advisor = json.loads(raw)
        # Ensure all five keys are present
        required = {"summary", "clothing", "rain_advice", "outdoor_activity", "advisory"}
        if not required.issubset(advisor.keys()):
            raise ValueError("Incomplete advisor keys")
        return advisor
    except Exception:
        return _fallback_insight(city, temp, humidity, wind_speed, predicted_temp, rain_probability_pct, will_rain)
