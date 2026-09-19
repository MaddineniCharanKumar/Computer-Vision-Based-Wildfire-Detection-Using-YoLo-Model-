import { AreaChart, Area, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'

const overview = [
  { name: 'Risk', value: 73 },
  { name: 'Confidence', value: 88 },
  { name: 'Guards', value: 4 },
  { name: 'GPU', value: 67 },
]

const history = [
  { time: '00:00', risk: 34, confidence: 0.62 },
  { time: '00:05', risk: 48, confidence: 0.70 },
  { time: '00:10', risk: 62, confidence: 0.77 },
  { time: '00:15', risk: 74, confidence: 0.83 },
]

export default function App() {
  return (
    <div className="app-shell">
      <header>
        <div>
          <div className="eyebrow">FIREGUARD AI</div>
          <h1>Wildfire Intelligence Dashboard</h1>
        </div>
        <div className="badge demo">DEMO MODE</div>
      </header>

      <section className="cards-grid">
        <div className="card">
          <h3>Overview</h3>
          <ul>
            {overview.map(item => (
              <li key={item.name}><span>{item.name}</span><strong>{item.value}</strong></li>
            ))}
          </ul>
        </div>
        <div className="card">
          <h3>Live Detection</h3>
          <p>Confidence 93%</p>
          <p>Persisted 12 seconds</p>
          <p>Growth +42%</p>
        </div>
        <div className="card">
          <h3>Environmental Monitoring</h3>
          <p>Wind 24 km/h</p>
          <p>Humidity 31%</p>
          <p>Visibility 8.5 km</p>
        </div>
      </section>

      <section className="charts-grid">
        <div className="card chart-card">
          <h3>Risk Trend</h3>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={history}>
              <defs>
                <linearGradient id="riskFill" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="5%" stopColor="#ff5d5d" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#ff5d5d" stopOpacity={0.2} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Area type="monotone" dataKey="risk" stroke="#ff5d5d" fill="url(#riskFill)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="card chart-card">
          <h3>Confidence</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={history}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis domain={[0, 1]} />
              <Tooltip />
              <Bar dataKey="confidence" fill="#4ade80" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>
  )
}
