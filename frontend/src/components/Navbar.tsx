import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Sparkles, Users, Flame, Calendar } from 'lucide-react';

interface NavbarProps {
  currentEventName?: string;
}

export const Navbar: React.FC<NavbarProps> = ({ currentEventName }) => {
  const location = useLocation();

  return (
    <nav className="navbar">
      <div className="nav-content">
        <Link to="/" className="brand-logo">
          <Sparkles className="text-amber-400" size={22} color="#f59e0b" />
          <span className="brand-badge">Raaso</span>
        </Link>

        <div className="nav-links">
          <Link
            to="/"
            className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
            title="Browse Events"
          >
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
              <Calendar size={15} /> Events
            </span>
          </Link>
          <Link
            to="/matches"
            className={`nav-link ${location.pathname === '/matches' ? 'active' : ''}`}
            title="Discover Matches"
          >
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
              <Flame size={15} /> Matches
            </span>
          </Link>
          <Link
            to="/squads"
            className={`nav-link ${location.pathname.startsWith('/squads') ? 'active' : ''}`}
            title="Event Squads"
          >
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
              <Users size={15} /> Squads
            </span>
          </Link>
        </div>
      </div>

      {currentEventName && (
        <div style={{
          fontSize: '0.75rem',
          color: '#fbbf24',
          marginTop: '6px',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '2px 8px',
          background: 'rgba(245, 158, 11, 0.1)',
          borderRadius: '4px',
          width: 'fit-content'
        }}>
          <span>📍</span>
          <span>Selected: <strong>{currentEventName}</strong></span>
        </div>
      )}
    </nav>
  );
};

