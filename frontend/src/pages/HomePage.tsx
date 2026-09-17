import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Calendar, MapPin, Search, ArrowRight, Music, Users, Shield } from 'lucide-react';
import { api } from '../api/client';
import type { Event } from '../lib/types';

export const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const [events, setEvents] = useState<Event[]>([]);
  const [filteredEvents, setFilteredEvents] = useState<Event[]>([]);
  const [cityFilter, setCityFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadEvents() {
      try {
        setIsLoading(true);
        const data = await api.getEvents();
        setEvents(data);
        setFilteredEvents(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load events.');
      } finally {
        setIsLoading(false);
      }
    }
    loadEvents();
  }, []);

  useEffect(() => {
    let result = events;
    if (cityFilter) {
      result = result.filter((e) =>
        e.city.toLowerCase().includes(cityFilter.toLowerCase())
      );
    }
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (e) => e.name.toLowerCase().includes(q) || e.venue.toLowerCase().includes(q)
      );
    }
    setFilteredEvents(result);
  }, [cityFilter, searchQuery, events]);

  const cities = Array.from(new Set(events.map((e) => e.city)));

  const handleSelectEvent = (event: Event) => {
    localStorage.setItem('raaso_active_event', JSON.stringify(event));
    navigate(`/events/${event.id}/onboard`);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      {/* Hero Section */}
      <section
        className="card"
        style={{
          textAlign: 'center',
          padding: '36px 20px',
          background: 'linear-gradient(180deg, rgba(35, 27, 54, 0.95) 0%, rgba(20, 16, 32, 0.9) 100%)',
          border: '1px solid rgba(245, 158, 11, 0.25)',
        }}
      >
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            background: 'rgba(245, 158, 11, 0.15)',
            border: '1px solid rgba(245, 158, 11, 0.3)',
            borderRadius: '9999px',
            padding: '4px 14px',
            fontSize: '0.8rem',
            color: '#fbbf24',
            fontWeight: 600,
            marginBottom: '14px',
          }}
        >
          <Sparkles size={14} />
          <span>Navratri & Dandiya Squad Finder</span>
        </div>

        <h1
          style={{
            fontSize: '2rem',
            fontWeight: 800,
            lineHeight: 1.2,
            marginBottom: '10px',
            letterSpacing: '-0.5px',
          }}
        >
          Find your people.{' '}
          <span
            style={{
              background: 'linear-gradient(135deg, #f59e0b, #f43f5e)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            Find your rhythm.
          </span>
        </h1>

        <p
          style={{
            fontSize: '0.95rem',
            color: '#94a3b8',
            maxWidth: '520px',
            margin: '0 auto 24px auto',
          }}
        >
          Going to a Garba night solo or looking for fellow dancers to form a 6-person circle?
          Match by dance energy, groove style, and squad up safely on WhatsApp.
        </p>

        {/* Feature Pills */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            flexWrap: 'wrap',
            gap: '12px',
            fontSize: '0.82rem',
            color: '#cbd5e1',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Music size={15} color="#f59e0b" />
            <span>Event-based Matching</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Users size={15} color="#f43f5e" />
            <span>Squad Formation</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Shield size={15} color="#10b981" />
            <span>Privacy-First & Safe</span>
          </div>
        </div>
      </section>

      {/* Events Listing */}
      <section>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '16px',
            flexWrap: 'wrap',
            gap: '10px',
          }}
        >
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Choose Your Event</h2>
            <p style={{ fontSize: '0.82rem', color: '#94a3b8' }}>
              Select where you are heading to discover compatible attendees
            </p>
          </div>

          {/* City Filter Pills */}
          {cities.length > 0 && (
            <div style={{ display: 'flex', gap: '6px', overflowX: 'auto', paddingBottom: '4px' }}>
              <button
                className={`chip-btn ${cityFilter === '' ? 'selected' : ''}`}
                onClick={() => setCityFilter('')}
              >
                All Cities
              </button>
              {cities.map((city) => (
                <button
                  key={city}
                  className={`chip-btn ${cityFilter === city ? 'selected' : ''}`}
                  onClick={() => setCityFilter(city)}
                >
                  {city}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Search Bar */}
        <div style={{ position: 'relative', marginBottom: '16px' }}>
          <Search
            size={18}
            color="#94a3b8"
            style={{ position: 'absolute', left: '14px', top: '14px' }}
          />
          <input
            type="text"
            className="form-input"
            style={{ paddingLeft: '42px' }}
            placeholder="Search event name or venue..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {isLoading ? (
          <div className="empty-state">
            <div className="spinner" />
            <p style={{ marginTop: '12px' }}>Loading Garba events...</p>
          </div>
        ) : error ? (
          <div className="card" style={{ textAlign: 'center', color: '#fda4af' }}>
            <p>{error}</p>
          </div>
        ) : filteredEvents.length === 0 ? (
          <div className="card empty-state">
            <Calendar size={36} className="empty-state-icon" />
            <h3>No events found</h3>
            <p style={{ fontSize: '0.85rem', marginTop: '6px' }}>
              Try adjusting your city filter or search query.
            </p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {filteredEvents.map((event) => {
              const startDate = new Date(event.starts_at);
              const formattedDate = startDate.toLocaleDateString(undefined, {
                weekday: 'short',
                month: 'short',
                day: 'numeric',
              });
              const formattedTime = startDate.toLocaleTimeString(undefined, {
                hour: '2-digit',
                minute: '2-digit',
              });

              return (
                <div
                  key={event.id}
                  className="card card-clickable"
                  onClick={() => handleSelectEvent(event)}
                  style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}
                >
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      justifyContent: 'space-between',
                      gap: '12px',
                    }}
                  >
                    <div>
                      <span className="badge badge-gold" style={{ marginBottom: '8px' }}>
                        {event.city}
                      </span>
                      <h3 style={{ fontSize: '1.15rem', fontWeight: 700, lineHeight: 1.3 }}>
                        {event.name}
                      </h3>
                    </div>
                    <div
                      style={{
                        background: 'rgba(255, 255, 255, 0.06)',
                        padding: '6px 12px',
                        borderRadius: '8px',
                        textAlign: 'center',
                        flexShrink: 0,
                      }}
                    >
                      <div style={{ fontSize: '0.75rem', color: '#fbbf24', fontWeight: 700 }}>
                        {formattedDate}
                      </div>
                      <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>
                        {formattedTime}
                      </div>
                    </div>
                  </div>

                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      fontSize: '0.85rem',
                      color: '#94a3b8',
                    }}
                  >
                    <MapPin size={15} color="#94a3b8" />
                    <span>{event.venue}</span>
                  </div>

                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      paddingTop: '8px',
                      borderTop: '1px solid rgba(255, 255, 255, 0.06)',
                      marginTop: '4px',
                    }}
                  >
                    <span style={{ fontSize: '0.8rem', color: '#fbbf24', fontWeight: 600 }}>
                      Find Squad & Matches
                    </span>
                    <div
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                        fontSize: '0.85rem',
                        fontWeight: 700,
                        color: '#f59e0b',
                      }}
                    >
                      <span>Enter Event</span>
                      <ArrowRight size={16} />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
};

