export default function MapPanel({ event }) {
  return (
    <div className="map-panel">
      <h3>Live Map</h3>
      <div className="map-placeholder">
        <div className="map-dot" />
        <div className="map-ring" />
        <div className="map-wind" />
        <p>Current fire + 30/60 min spread preview</p>
      </div>
      {event && (
        <div className="map-meta">
          <span>Latitude: {event.latitude}</span>
          <span>Longitude: {event.longitude}</span>
          <span>Risk: {event.riskScore}</span>
        </div>
      )}
    </div>
  )
}
