import { useEffect, useMemo, useRef, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const GOOGLE_MAPS_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ''
const DEFAULT_LOCATION = {
  latitude: Number(import.meta.env.VITE_MAP_LATITUDE || 20.5937),
  longitude: Number(import.meta.env.VITE_MAP_LONGITUDE || 78.9629),
  label: import.meta.env.VITE_MAP_LOCATION_LABEL || 'Configured monitoring area',
}

function loadGoogleMaps(key) {
  if (!key) return Promise.reject(new Error('VITE_GOOGLE_MAPS_API_KEY is not configured'))
  if (window.google?.maps) return Promise.resolve(window.google.maps)
  if (window.__googleMapsPromise) return window.__googleMapsPromise

  window.__googleMapsPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(key)}&v=weekly`
    script.async = true
    script.defer = true
    script.onload = () => resolve(window.google.maps)
    script.onerror = () => reject(new Error('Google Maps failed to load'))
    document.head.appendChild(script)
  })
  return window.__googleMapsPromise
}

function GoogleMap({ location, forecastDirection }) {
  const mapRef = useRef(null)
  const mapInstance = useRef(null)
  const markerInstance = useRef(null)
  const directionLine = useRef(null)
  const [mapError, setMapError] = useState('')

  useEffect(() => {
    let cancelled = false
    loadGoogleMaps(GOOGLE_MAPS_KEY)
      .then((maps) => {
        if (cancelled || !mapRef.current) return
        const center = { lat: location.latitude, lng: location.longitude }
        mapInstance.current = new maps.Map(mapRef.current, {
          center,
          zoom: 13,
          mapTypeId: 'hybrid',
          streetViewControl: false,
          mapTypeControl: true,
          fullscreenControl: true,
        })
        markerInstance.current = new maps.Marker({
          map: mapInstance.current,
          position: center,
          title: location.label,
          label: { text: 'FIRE', color: '#ffffff', fontWeight: '700' },
        })
        new maps.Circle({
          map: mapInstance.current,
          center,
          radius: 800,
          strokeColor: '#ef4444',
          strokeOpacity: 0.85,
          fillColor: '#ef4444',
          fillOpacity: 0.15,
        })
      })
      .catch((error) => {
        if (!cancelled) setMapError(error.message)
      })
    return () => { cancelled = true }
  }, [location.latitude, location.longitude, location.label])

  useEffect(() => {
    if (!mapInstance.current || !window.google?.maps) return
    const maps = window.google.maps
    const vectors = { NORTH: [0, 0.012], EAST: [0.012, 0], SOUTH: [0, -0.012], WEST: [-0.012, 0] }
    const [latDelta, lngDelta] = vectors[forecastDirection] || [0, 0]
    const start = { lat: location.latitude, lng: location.longitude }
    const end = { lat: location.latitude + latDelta, lng: location.longitude + lngDelta }
    directionLine.current?.setMap(null)
    directionLine.current = new maps.Polyline({
      map: mapInstance.current,
      path: [start, end],
      geodesic: true,
      strokeColor: '#f59e0b',
      strokeOpacity: 0.95,
      strokeWeight: 5,
      icons: [{ icon: { path: maps.SymbolPath.FORWARD_CLOSED_ARROW }, offset: '100%' }],
    })
  }, [forecastDirection, location.latitude, location.longitude])

  if (mapError) {
    return <div className="map-placeholder"><strong>Google Maps unavailable</strong><span>{mapError}</span><small>Configure VITE_GOOGLE_MAPS_API_KEY and enable Maps JavaScript API.</small></div>
  }
  return <div ref={mapRef} className="google-map" aria-label="Google map showing the monitoring location" />
}

function Value({ value, unit = '' }) {
  return value === null || value === undefined ? <span className="unavailable">Unavailable</span> : <>{value}{unit}</>
}

export default function App() {
  const [location, setLocation] = useState(DEFAULT_LOCATION)
  const [environment, setEnvironment] = useState(null)
  const [health, setHealth] = useState(null)
  const [error, setError] = useState('')

  const refresh = async () => {
    try {
      const query = `latitude=${location.latitude}&longitude=${location.longitude}`
      const [environmentResponse, healthResponse] = await Promise.all([
        fetch(`${API_BASE}/api/environment/current?${query}`),
        fetch(`${API_BASE}/api/health`),
      ])
      if (!environmentResponse.ok) throw new Error(`Environment request failed (${environmentResponse.status})`)
      setEnvironment(await environmentResponse.json())
      if (healthResponse.ok) setHealth(await healthResponse.json())
      setError('')
    } catch (requestError) {
      setError(requestError.message)
    }
  }

  useEffect(() => { refresh(); const timer = setInterval(refresh, 60000); return () => clearInterval(timer) }, [location.latitude, location.longitude])

  const windDirection = environment?.wind_direction
  const direction = useMemo(() => {
    if (windDirection === null || windDirection === undefined) return 'Unavailable'
    const names = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    return names[Math.round(windDirection / 45) % 8]
  }, [windDirection])

  const forecastDirection = direction === 'Unavailable' ? null : ({ N: 'NORTH', NE: 'NORTH', E: 'EAST', SE: 'SOUTH', S: 'SOUTH', SW: 'SOUTH', W: 'WEST', NW: 'NORTH' }[direction])
  const status = environment?.freshness || 'UNAVAILABLE'

  return (
    <main className="app-shell">
      <header>
        <div><div className="eyebrow">ECOSPREAD-YOLO</div><h1>Wildfire Intelligence Dashboard</h1><p className="subtitle">Live environmental context and directional spread assessment</p></div>
        <div className={`badge ${status.toLowerCase()}`}>{status}</div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <section className="location-layout">
        <div className="card map-card"><div className="section-heading"><div><h2>Geospatial monitor</h2><p>Google Maps satellite/hybrid view</p></div><button onClick={refresh}>Refresh</button></div><GoogleMap location={location} forecastDirection={forecastDirection} /></div>
        <aside className="card location-card"><h2>Monitoring location</h2><div className="location-pin">●</div><h3>{location.label}</h3><p className="coordinates">{location.latitude.toFixed(6)}, {location.longitude.toFixed(6)}</p><dl><div><dt>Source</dt><dd>{environment?.source || 'Unavailable'}</dd></div><div><dt>Observation</dt><dd>{environment?.timestamp || 'Unavailable'}</dd></div><div><dt>Map status</dt><dd>{GOOGLE_MAPS_KEY ? 'Configured' : 'API key required'}</dd></div><div><dt>Backend</dt><dd>{health?.status || 'Unavailable'}</dd></div></dl><p className="notice">Coordinates are supplied by configuration. No location is invented by the dashboard.</p></aside>
      </section>

      <section className="card"><div className="section-heading"><div><h2>Environmental factors</h2><p>Values are read from the configured live provider.</p></div><span className={`status-dot ${status.toLowerCase()}`}>{status}</span></div><div className="environment-grid">
        <div><span>Temperature</span><strong><Value value={environment?.temperature} unit=" °C" /></strong></div><div><span>Relative humidity</span><strong><Value value={environment?.humidity} unit=" %" /></strong></div><div><span>Wind speed</span><strong><Value value={environment?.wind_speed} unit=" km/h" /></strong></div><div><span>Wind direction</span><strong><Value value={environment?.wind_direction} unit="°" /> {direction !== 'Unavailable' && `(${direction})`}</strong></div><div><span>Precipitation</span><strong><Value value={environment?.rainfall} unit=" mm" /></strong></div><div><span>Pressure</span><strong><Value value={environment?.pressure} unit=" hPa" /></strong></div><div><span>PM2.5</span><strong><Value value={environment?.pm25} unit=" μg/m³" /></strong></div><div><span>PM10</span><strong><Value value={environment?.pm10} unit=" μg/m³" /></strong></div><div><span>Visibility</span><strong><Value value={environment?.visibility} unit=" km" /></strong></div>
      </div></section>

      <section className="cards-grid"><div className="card spread-card"><h2>Likely spread direction</h2><div className="direction-arrow">{forecastDirection || '—'}</div><h3>{forecastDirection || 'Unavailable'}</h3><p>Wind direction is used as an engineering indicator only. A validated forecast model and calibrated perimeter are required for operational decisions.</p></div><div className="card"><h2>Provider health</h2><p><strong>{environment?.source || 'UNAVAILABLE'}</strong></p><p>{environment?.message || 'Live provider response received.'}</p><p className="muted">Updates every 60 seconds.</p></div></section>
    </main>
  )
}
