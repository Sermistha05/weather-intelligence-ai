import { useState } from 'react'
import './App.css'
import {
  ResponsiveContainer, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip
} from 'recharts'

function App() {
  const [city, setCity] = useState('')
  const [weather, setWeather] = useState(null)
  const [temperaturePrediction, setTemperaturePrediction] = useState(null)
  const [rainPrediction, setRainPrediction] = useState(null)
  const [historyData, setHistoryData] = useState(null)
  const [historyLoading, setHistoryLoading] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  

  const searchWeather = async () => {
    if (!city.trim()) return

    setLoading(true)
    setError('')
    setTemperaturePrediction(null)
    setRainPrediction(null)
    setHistoryData(null)

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
    }

    try {
      const rainResponse = await fetch(
        `http://127.0.0.1:8000/predict/rain/by-city?city=${encodeURIComponent(city)}`
      )
      if (!rainResponse.ok) throw new Error('Rain prediction failed')
      const rainData = await rainResponse.json()
      setRainPrediction(rainData)
    } catch (err) {
      console.error('Rain prediction error:', err)
    } finally {
      setLoading(false)
    }

    setHistoryLoading(true)
    try {
      const historyResponse = await fetch(
        `http://127.0.0.1:8000/weather/history?city=${encodeURIComponent(city)}&limit=50`
      )
      if (!historyResponse.ok) throw new Error('History fetch failed')
      const raw = await historyResponse.json()
      setHistoryData([...raw].reverse())
    } catch (err) {
      console.error('Weather history error:', err)
      setHistoryData([])
    } finally {
      setHistoryLoading(false)
    }
  }

  const formatTimestamp = (ts) => {
    if (!ts) return ''
    const d = new Date(ts)
    return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
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
                  {rainPrediction === null
                    ? 'Loading...'
                    : `${rainPrediction.rain_probability_pct}%`}
                </strong>
                {rainPrediction !== null && (
                  <p style={{ marginTop: '8px', fontSize: '14px', color: rainPrediction.will_rain ? '#f87171' : '#4ade80' }}>
                    {rainPrediction.will_rain ? 'Rain Expected' : 'No Rain Expected'}
                  </p>
                )}
              </div>
            </section>

            <section className="history-card">
              <h2>Weather History Analytics</h2>
              <p className="history-subtitle">{weather.location} — Last 50 records</p>

              {historyLoading && (
                <p className="history-state">Loading history...</p>
              )}

              {!historyLoading && historyData && historyData.length === 0 && (
                <p className="history-state">No historical data available for this city.</p>
              )}

              {!historyLoading && historyData && historyData.length > 0 && (
                <div className="charts-grid">

                  <div className="chart-block">
                    <h3>Temperature Trend</h3>
                    <ResponsiveContainer width="100%" height={220}>
                      <LineChart data={historyData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.1)" />
                        <XAxis dataKey="timestamp" tickFormatter={formatTimestamp} tick={{ fill: '#94a3b8', fontSize: 11 }} interval={9} />
                        <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} unit="°C" width={45} />
                        <Tooltip
                          contentStyle={{ background: '#111c2d', border: '1px solid #26364d', borderRadius: '8px' }}
                          labelStyle={{ color: '#94a3b8', fontSize: '12px' }}
                          labelFormatter={formatTimestamp}
                          formatter={(v) => [`${v}°C`, 'Temperature']}
                        />
                        <Line type="monotone" dataKey="temperature" stroke="#38bdf8" dot={false} strokeWidth={2} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="chart-block">
                    <h3>Humidity Trend</h3>
                    <ResponsiveContainer width="100%" height={220}>
                      <LineChart data={historyData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.1)" />
                        <XAxis dataKey="timestamp" tickFormatter={formatTimestamp} tick={{ fill: '#94a3b8', fontSize: 11 }} interval={9} />
                        <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} unit="%" width={40} />
                        <Tooltip
                          contentStyle={{ background: '#111c2d', border: '1px solid #26364d', borderRadius: '8px' }}
                          labelStyle={{ color: '#94a3b8', fontSize: '12px' }}
                          labelFormatter={formatTimestamp}
                          formatter={(v) => [`${v}%`, 'Humidity']}
                        />
                        <Line type="monotone" dataKey="humidity" stroke="#818cf8" dot={false} strokeWidth={2} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="chart-block chart-block--full">
                    <h3>Rain Events</h3>
                    <ResponsiveContainer width="100%" height={160}>
                      <BarChart data={historyData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.1)" />
                        <XAxis dataKey="timestamp" tickFormatter={formatTimestamp} tick={{ fill: '#94a3b8', fontSize: 11 }} interval={9} />
                        <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} ticks={[0, 1]} tickFormatter={(v) => v === 1 ? 'Rain' : 'Dry'} width={40} />
                        <Tooltip
                          contentStyle={{ background: '#111c2d', border: '1px solid #26364d', borderRadius: '8px' }}
                          labelStyle={{ color: '#94a3b8', fontSize: '12px' }}
                          labelFormatter={formatTimestamp}
                          formatter={(v) => [v === 1 ? 'Rain Event' : 'No Rain', 'Rain Event']}
                        />
                        <Bar dataKey="rain" fill="#38bdf8" opacity={0.8} radius={[3, 3, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>

                </div>
              )}
            </section>
          </>
        )}
      </main>
    </div>
  )
}

export default App