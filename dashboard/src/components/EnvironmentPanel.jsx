export default function EnvironmentPanel({ environment }) {
  return (
    <div className="environment-panel">
      <h3>Environment</h3>
      <div className="stats-grid">
        <div>Temp: {environment?.temperatureC ?? 'N/A'}°C</div>
        <div>Humidity: {environment?.humidityPct ?? 'N/A'}%</div>
        <div>Wind: {environment?.windSpeedKmh ?? 'N/A'} km/h</div>
        <div>Direction: {environment?.windDirectionDeg ?? 'N/A'}°</div>
        <div>Rain: {environment?.rainfallMm ?? 'N/A'} mm</div>
        <div>Pressure: {environment?.pressureHpa ?? 'N/A'} hPa</div>
      </div>
    </div>
  )
}
