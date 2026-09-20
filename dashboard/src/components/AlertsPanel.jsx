export default function AlertsPanel({ alerts }) {
  return (
    <div className="alerts-panel">
      {alerts.length === 0 ? (
        <p>No alerts yet.</p>
      ) : (
        alerts.map((alert) => (
          <div className="alert-row" key={alert.alertId}>
            <strong>{alert.level}</strong>
            <div>{alert.title}</div>
            <small>{alert.message}</small>
          </div>
        ))
      )}
    </div>
  )
}
