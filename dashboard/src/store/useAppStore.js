import { create } from 'zustand'

const useAppStore = create((set, get) => ({
  system: {
    online: true,
    demoMode: false,
    modelStatus: 'ready',
    providerStatus: 'LIVE',
    gpu: {
      device: 'cuda',
      utilization: 87,
      memoryUsedGb: 9.4,
      memoryTotalGb: 24,
      temperatureC: 61,
      fps: 81,
      cudaAvailable: true,
      precision: 'fp16',
    },
  },

  environment: {
    timestamp: null,
    source: 'OPEN_METEO',
    freshness: 'LIVE',
    status: 'LIVE',
    temperatureC: 32.5,
    humidityPct: 31.0,
    windSpeedKmh: 22.0,
    windDirectionDeg: 210,
    rainfallMm: 0.0,
    pressureHpa: 1012.0,
    pm25: 18.5,
    pm10: 25.0,
    visibilityKm: 8.5,
    isDemo: false,
  },

  cameras: [
    { id: 'uav-01', name: 'UAV-01', status: 'LIVE', gpsLocked: true, battery: 72, altitudeM: 126, speedKmh: 18 },
    { id: 'cctv-01', name: 'CCTV-01', status: 'LIVE', gpsLocked: false, battery: null, altitudeM: null, speedKmh: null },
  ],

  fireEvents: [
    {
      eventId: 'F-2026-0091',
      cameraId: 'uav-01',
      status: 'ACTIVE',
      latitude: 14.1234,
      longitude: 77.5678,
      confidence: 0.947,
      riskScore: 82,
      growthRate: 18.4,
      spreadDirection: 'NE',
      visualAreaProxy: 12480,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
  ],

  forecasts: [
    { eventId: 'F-2026-0091', horizonMinutes: 30, confidence: 0.8, polygon: '...' },
    { eventId: 'F-2026-0091', horizonMinutes: 60, confidence: 0.7, polygon: '...' },
  ],

  alerts: [
    {
      alertId: 'AL-001',
      eventId: 'F-2026-0091',
      level: 'HIGH',
      title: 'High risk fire',
      message: 'Fire persisted and wind increased.',
      acknowledged: false,
      createdAt: new Date().toISOString(),
    }
  ],

  ws: {
    connected: false,
    lastEventAt: null,
  },

  fetchEnvironment: async () => {
    const res = await fetch('http://localhost:8000/api/environment/current?latitude=14.1234&longitude=77.5678')
    const json = await res.json()
    set({ environment: json })
  },

  fetchSystem: async () => {
    const res = await fetch('http://localhost:8000/api/health')
    const json = await res.json()
    set({ system: { ...get().system, ...json } })
  },

  connectWebSocket: () => {
    const socket = new WebSocket('ws://localhost:8000/ws/live')
    socket.onopen = () => set({ ws: { connected: true, lastEventAt: Date.now() } })
    socket.onclose = () => set({ ws: { connected: false, lastEventAt: Date.now() } })
    socket.onmessage = (event) => {
      const msg = JSON.parse(event.data)
      console.log('WS message', msg)
    }
  },
}))

export default useAppStore
