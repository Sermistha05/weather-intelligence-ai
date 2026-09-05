import { useState } from 'react'
import './App.css'

function App() {
  const [city, setCity] = useState('')
  const [weather, setWeather] = useState(null)
  const [temperaturePrediction, setTemperaturePrediction] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  

  const searchWeather = async () => {
    if (!city.trim()) return

    setLoading(true)
    setError('')
    setTemperaturePrediction(null)

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/weather/current?city=${encodeURIComponent(city)}`
      )

      if (!response.ok) {
        throw new Error('Weather data not found')
      }

      const data = await response.json()
      setWeather(data)
    } catch (err) {
      setError('Unable to fetch weather data. Please check the city name.')
      setWeather(null)
      setLoading(false)
      return
    }

    try {
      const predictionResponse = await fetch(
        `http://127.0.0.1:8000/predict/temperature/by-city?city=${encodeURIComponent(city)}`
      )

      if (!predictionResponse.ok) {
        throw new Error('Temperature prediction failed')
      }

      const predictionData = await predictionResponse.json()
      const predictedTemperature =
        typeof predictionData === 'number'
          ? predictionData
          : predictionData.predicted_temperature ??
            predictionData.temperature ??
            predictionData.prediction ??
            predictionData.value ??
            null

      setTemperaturePrediction(predictedTemperature)
    } catch (err) {
      console.error('Temperature prediction error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Sky Sense</h1>
          <p>Weather Intelligence at a Glance</p>
        </div>

        <div className="status">
          ● System Online
        </div>
      </header>

      <main className="dashboard">
        <section className="search-section">
          <h2>Weather Overview</h2>

          <div className="search-box">
            <input
              type="text"
              placeholder="Enter city name..."
              value={city}
              onChange={(e) => setCity(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  searchWeather()
                }
              }}
            />

            <button onClick={searchWeather} disabled={loading}>
              {loading ? 'Loading...' : 'Search'}
            </button>
          </div>

          {error && <p className="error">{error}</p>}
        </section>

        {weather && (
          <>
            <section className="weather-card">
              <div>
                <p className="location">
                  {weather.location}
                </p>

                <h2>{weather.temperature}°C</h2>

                <p>
                  {weather.rain ? 'Rain Detected' : 'No Rain'}
                </p>
              </div>

              <div className="weather-details">
                <div>
                  <span>Humidity</span>
                  <strong>{weather.humidity}%</strong>
                </div>

                <div>
                  <span>Pressure</span>
                  <strong>{weather.pressure} hPa</strong>
                </div>

                <div>
                  <span>Wind Speed</span>
                  <strong>{weather.wind_speed} km/h</strong>
                </div>

                <div>
                  <span>UV Index</span>
                  <strong>{weather.uv_index}</strong>
                </div>
              </div>
            </section>

            <section className="prediction-grid">
              <div className="prediction-card">
                <span>🌡️</span>
                <h3>Temperature Prediction</h3>
                <p>AI predicted temperature</p>
                <strong>{temperaturePrediction !== null? `${temperaturePrediction}°C`: 'Loading...'}</strong>
              </div>

              <div className="prediction-card">
                <span>🌧️</span>
                <h3>Rain Prediction</h3>
                <p>AI precipitation analysis</p>
                <strong>
                  {weather.rain_probability}%
                </strong>
              </div>
            </section>

            <section className="history-card">
              <h2>Weather History</h2>
              <p>
                Historical weather analytics will appear here.
              </p>
            </section>
          </>
        )}
      </main>
    </div>
  )
}

export default App