import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import CommandCenterPage from './pages/CommandCenterPage'
import MapPage from './pages/MapPage'
import FireEventsPage from './pages/FireEventsPage'
import EnvironmentPage from './pages/EnvironmentPage'
import SpreadPredictionPage from './pages/SpreadPredictionPage'
import AlertsPage from './pages/AlertsPage'
import AnalyticsPage from './pages/AnalyticsPage'
import SystemPage from './pages/SystemPage'

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<CommandCenterPage />} />
          <Route path="/map" element={<MapPage />} />
          <Route path="/fires" element={<FireEventsPage />} />
          <Route path="/environment" element={<EnvironmentPage />} />
          <Route path="/spread" element={<SpreadPredictionPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/system" element={<SystemPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}
