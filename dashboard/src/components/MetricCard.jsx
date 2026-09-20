export default function MetricCard({ label, value, unit = '' }) {
  return (
    <div className="metric-card">
      <div className="metric-label">{label}</div>
      <div className="metric-value">
        {value}
        {unit}
      </div>
    </div>
  )
}
