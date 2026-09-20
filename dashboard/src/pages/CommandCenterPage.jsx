import { useEffect } from 'react'
import useAppStore from '../store/useAppStore'
import MetricCard from '../components/MetricCard'
import MapPanel from '../components/MapPanel'
import EnvironmentPanel from '../components/EnvironmentPanel'
import AlertsPanel from '../components/AlertsPanel'
import VideoPanel from '../components/VideoPanel'

export default function CommandCenterPage() {
  const { environment, system, fireEvents, alerts, fetchEnvironment, fetchSystem } = useAppStore()

  useEffect(() => {
    fetchEnvironment()
    fetchSystem()
  }, [fetchEnvironment, fetchSystem])

  const activeEvent = fireEvents[0]

  return (
    <div className="page-grid">
      <div className="card card-large">
        <VideoPanel />
      </div>

      <div className="card">
        <h3>Fire Risk</h3>
        <div className="risk-score">{activeEvent?.riskScore ?? 0}</div>
        <p>{activeEvent?.status ?? 'NO EVENT'}</p>
      </div>

      <div className="card">
        <EnvironmentPanel environment={environment} />
      </div>

      <div className="card card-wide">
        <MapPanel event={activeEvent} />
      </div>

      <div className="card">
        <h3>Alerts</h3>
        <AlertsPanel alerts={alerts} />
      </div>

      <div className="card">
        <h3>System</h3>
        <MetricCard label="GPU" value={`${system.gpu.utilization}%`} />
        <MetricCard label="Model" value={system.modelStatus} />
      </div>
    </div>
  )
}
