import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Users,
  Flame,
  MessageCircle,
  ShieldAlert,
  ArrowRight,
  RefreshCw,
  Sparkles,
  CheckCircle2,
} from 'lucide-react';
import { api } from '../api/client';
import { ReportModal } from '../components/ReportModal';
import type { MatchDetail, User, Event } from '../lib/types';

export const MatchesPage: React.FC = () => {
  const navigate = useNavigate();

  const [matches, setMatches] = useState<MatchDetail[]>([]);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [activeEvent, setActiveEvent] = useState<Event | null>(null);
  const [attendanceId, setAttendanceId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Reporting modal state
  const [reportModalUser, setReportModalUser] = useState<{ id: string; name: string } | null>(null);

  const loadMatches = async () => {
    const storedUserStr = localStorage.getItem('raaso_user');
    const storedAttId = localStorage.getItem('raaso_attendance_id');
    const storedEventStr = localStorage.getItem('raaso_active_event');

    if (!storedUserStr || !storedAttId) {
      setIsLoading(false);
      return;
    }

    try {
      setCurrentUser(JSON.parse(storedUserStr));
      setAttendanceId(storedAttId);
      if (storedEventStr) {
        setActiveEvent(JSON.parse(storedEventStr));
      }

      setIsLoading(true);
      setError(null);
      const data = await api.getMatches(storedAttId);
      setMatches(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch matches.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadMatches();
  }, []);

  if (!attendanceId || !currentUser) {
    return (
      <div className="card empty-state" style={{ padding: '48px 20px' }}>
        <Sparkles size={40} color="#f59e0b" style={{ marginBottom: '16px' }} />
        <h2 style={{ fontSize: '1.4rem', fontWeight: 800, marginBottom: '8px' }}>
          Join an Event First
        </h2>
        <p style={{ color: '#94a3b8', maxWidth: '400px', margin: '0 auto 24px auto' }}>
          Select a Garba event and set up your dance energy profile to discover compatible attendees.
        </p>
        <button
          onClick={() => navigate('/')}
          className="btn btn-primary"
        >
          <span>Browse Garba Events</span>
          <ArrowRight size={16} />
        </button>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Event Header & Quick Switch */}
      <div
        className="card"
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '12px',
          background: 'linear-gradient(135deg, rgba(30, 24, 46, 0.9) 0%, rgba(18, 14, 28, 0.9) 100%)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
          <div>
            <span className="badge badge-gold" style={{ marginBottom: '4px' }}>
              {activeEvent ? activeEvent.city : 'Garba Event'}
            </span>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 800 }}>
              {activeEvent ? activeEvent.name : 'Event Matches'}
            </h2>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={loadMatches}
              className="btn btn-secondary btn-sm"
              title="Refresh matches"
            >
              <RefreshCw size={14} />
              <span>Refresh</span>
            </button>
            <Link
              to="/squads"
              className="btn btn-primary btn-sm"
            >
              <Users size={15} />
              <span>View Squads</span>
            </Link>
          </div>
        </div>

        <div style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span>Logged in as <strong>{currentUser.display_name}</strong></span>
          <span>•</span>
          <span>Matching based on your intent, dance skill & vibes</span>
        </div>
      </div>

      {/* Matches List */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Flame size={18} color="#f59e0b" />
            <span>Compatible Attendees ({matches.length})</span>
          </h3>
          <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>Ranked by rhythm compatibility</span>
        </div>

        {isLoading ? (
          <div className="empty-state">
            <div className="spinner" />
            <p style={{ marginTop: '12px' }}>Analyzing dance compatibility scores...</p>
          </div>
        ) : error ? (
          <div className="card" style={{ color: '#fda4af', textAlign: 'center' }}>
            <p>{error}</p>
          </div>
        ) : matches.length === 0 ? (
          <div className="card empty-state">
            <Users size={40} className="empty-state-icon" />
            <h3>No attendees yet</h3>
            <p style={{ fontSize: '0.85rem', marginTop: '6px', maxWidth: '420px', margin: '6px auto 16px auto' }}>
              You are among the first to register for this event! Share the event link or invite friends to join your squad.
            </p>
            <Link to="/squads" className="btn btn-primary btn-sm">
              Create a Squad
            </Link>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {matches.map((item) => {
              const u = item.matched_user;
              const att = item.matched_attendance;
              const score = item.score;

              return (
                <div
                  key={att.id}
                  className="card"
                  style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}
                >
                  <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '12px' }}>
                    <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                      <div className="score-badge" title={`${score}% Match Compatibility`}>
                        {score}%
                      </div>
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <h4 style={{ fontSize: '1.1rem', fontWeight: 700 }}>{u.display_name}</h4>
                          {u.age_bracket && (
                            <span className="badge badge-gray">{u.age_bracket}</span>
                          )}
                        </div>
                        <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '2px' }}>
                          📍 {u.city} • Dance Level: <strong style={{ color: '#fbbf24' }}>{att.dance_level}</strong>
                        </div>
                      </div>
                    </div>

                    <button
                      onClick={() => setReportModalUser({ id: u.id, name: u.display_name })}
                      title="Report attendee for safety concerns"
                      style={{ color: '#64748b', padding: '4px' }}
                    >
                      <ShieldAlert size={18} />
                    </button>
                  </div>

                  {/* Compatibility factors */}
                  <div
                    style={{
                      background: 'rgba(255, 255, 255, 0.04)',
                      padding: '10px 12px',
                      borderRadius: '8px',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '4px',
                    }}
                  >
                    <div style={{ fontSize: '0.72rem', color: '#fbbf24', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      Why you match:
                    </div>
                    {item.reasons.map((r, idx) => (
                      <div
                        key={idx}
                        style={{
                          fontSize: '0.82rem',
                          color: '#cbd5e1',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px',
                        }}
                      >
                        <CheckCircle2 size={13} color="#10b981" />
                        <span>{r}</span>
                      </div>
                    ))}
                  </div>

                  {/* Action Buttons */}
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      flexWrap: 'wrap',
                      gap: '10px',
                      paddingTop: '6px',
                    }}
                  >
                    {u.instagram_handle ? (
                      <a
                        href={`https://instagram.com/${u.instagram_handle.replace('@', '')}`}
                        target="_blank"
                        rel="noreferrer"
                        className="badge badge-purple"
                        style={{ padding: '6px 12px', fontSize: '0.8rem', gap: '6px' }}
                      >
                        <span>{u.instagram_handle}</span>
                      </a>
                    ) : (
                      <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                        Privacy protected
                      </span>
                    )}

                    {item.whatsapp_link && (
                      <a
                        href={item.whatsapp_link}
                        target="_blank"
                        rel="noreferrer"
                        className="btn btn-whatsapp btn-sm"
                      >
                        <MessageCircle size={16} />
                        <span>Connect on WhatsApp</span>
                      </a>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Safety Report Modal */}
      {reportModalUser && currentUser && (
        <ReportModal
          isOpen={true}
          onClose={() => setReportModalUser(null)}
          reportedUserId={reportModalUser.id}
          reportedUserName={reportModalUser.name}
          reporterId={currentUser.id}
        />
      )}
    </div>
  );
};

