import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Command Center' },
  { to: '/map', label: 'Live Map' },
  { to: '/fires', label: 'Fire Events' },
  { to: '/environment', label: 'Environment' },
  { to: '/spread', label: 'Spread Prediction' },
  { to: '/alerts', label: 'Alerts' },
  { to: '/analytics', label: 'Analytics' },
  { to: '/system', label: 'System' },
]

export default function Layout({ children }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">EcoSpread-YOLO</div>
        <nav>
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="main-panel">{children}</main>
    </div>
  )
}
