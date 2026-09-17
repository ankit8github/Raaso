import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Users,
  Plus,
  MessageCircle,
  LogOut,
  UserPlus,
  Sparkles,
  ArrowRight,
  Flame,
  X,
} from 'lucide-react';
import { api } from '../api/client';
import type { Squad, User, Event } from '../lib/types';

export const SquadPage: React.FC = () => {
  const navigate = useNavigate();

  const [squads, setSquads] = useState<Squad[]>([]);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [activeEvent, setActiveEvent] = useState<Event | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Create squad modal state
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [squadName, setSquadName] = useState('');
  const [maxMembers, setMaxMembers] = useState(6);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  // Selected squad details modal
  const [selectedSquad, setSelectedSquad] = useState<Squad | null>(null);

  const loadSquads = async () => {
    const storedUserStr = localStorage.getItem('raaso_user');
    const storedEventStr = localStorage.getItem('raaso_active_event');
    const storedEventId = localStorage.getItem('raaso_event_id');

    if (!storedUserStr || !storedEventId) {
      setIsLoading(false);
      return;
    }

    try {
      setCurrentUser(JSON.parse(storedUserStr));
      if (storedEventStr) {
        setActiveEvent(JSON.parse(storedEventStr));
      }

      setIsLoading(true);
      setError(null);
      const data = await api.getSquads(storedEventId);
      setSquads(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch event squads.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSquads();
  }, []);

  const handleCreateSquad = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentUser || !activeEvent) return;
    if (!squadName.trim()) {
      setFormError('Squad name is required.');
      return;
    }

    setIsSubmitting(true);
    setFormError(null);

    try {
      await api.createSquad({
        event_id: activeEvent.id,
        created_by: currentUser.id,
        name: squadName.trim(),
        max_members: maxMembers,
      });
      setSquadName('');
      setIsCreateOpen(false);
      await loadSquads();
    } catch (err: any) {
      setFormError(err.message || 'Failed to create squad.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleJoinSquad = async (squadId: string) => {
    if (!currentUser) return;
    try {
      await api.joinSquad(squadId, currentUser.id);
      await loadSquads();
      if (selectedSquad && selectedSquad.id === squadId) {
        const updated = await api.getSquad(squadId);
        setSelectedSquad(updated);
      }
    } catch (err: any) {
      alert(err.message || 'Failed to join squad.');
    }
  };

  const handleLeaveSquad = async (squadId: string) => {
    if (!currentUser) return;
    if (!window.confirm('Are you sure you want to leave this squad?')) return;

    try {
      await api.leaveSquad(squadId, currentUser.id);
      await loadSquads();
      if (selectedSquad && selectedSquad.id === squadId) {
        const updated = await api.getSquad(squadId);
        setSelectedSquad(updated);
      }
    } catch (err: any) {
      alert(err.message || 'Failed to leave squad.');
    }
  };

  const openSquadDetails = async (squadId: string) => {
    try {
      const data = await api.getSquad(squadId);
      setSelectedSquad(data);
    } catch (err: any) {
      alert(err.message || 'Failed to load squad details.');
    }
  };

  if (!currentUser || !activeEvent) {
    return (
      <div className="card empty-state" style={{ padding: '48px 20px' }}>
        <Users size={40} color="#f59e0b" style={{ marginBottom: '16px' }} />
        <h2 style={{ fontSize: '1.4rem', fontWeight: 800, marginBottom: '8px' }}>
          Select an Event First
        </h2>
        <p style={{ color: '#94a3b8', maxWidth: '400px', margin: '0 auto 24px auto' }}>
          Browse available Garba events to view and form festival squads.
        </p>
        <button onClick={() => navigate('/')} className="btn btn-primary">
          <span>Browse Garba Events</span>
          <ArrowRight size={16} />
        </button>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header */}
      <div
        className="card"
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '12px',
          background: 'linear-gradient(135deg, rgba(30, 24, 46, 0.9) 0%, rgba(18, 14, 28, 0.9) 100%)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
          <div>
            <span className="badge badge-gold" style={{ marginBottom: '4px' }}>
              {activeEvent.city}
            </span>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 800 }}>{activeEvent.name} Squads</h2>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <Link to="/matches" className="btn btn-secondary btn-sm">
              <Flame size={15} color="#f59e0b" />
              <span>Matches</span>
            </Link>
            <button
              onClick={() => setIsCreateOpen(true)}
              className="btn btn-primary btn-sm"
            >
              <Plus size={16} />
              <span>Create Squad</span>
            </button>
          </div>
        </div>
        <p style={{ fontSize: '0.82rem', color: '#94a3b8' }}>
          Form a circle, meet up at the entrance, and groove together! No private phone numbers shared.
        </p>
      </div>

      {/* Squads List */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Users size={18} color="#f43f5e" />
            <span>Active Squads ({squads.length})</span>
          </h3>
        </div>

        {isLoading ? (
          <div className="empty-state">
            <div className="spinner" />
            <p style={{ marginTop: '12px' }}>Loading event squads...</p>
          </div>
        ) : error ? (
          <div className="card" style={{ color: '#fda4af', textAlign: 'center' }}>
            <p>{error}</p>
          </div>
        ) : squads.length === 0 ? (
          <div className="card empty-state">
            <Users size={40} className="empty-state-icon" />
            <h3>No squads created yet</h3>
            <p style={{ fontSize: '0.85rem', marginTop: '6px', maxWidth: '400px', margin: '6px auto 16px auto' }}>
              Be the first to create a squad for this event and invite fellow dancers to circle up!
            </p>
            <button onClick={() => setIsCreateOpen(true)} className="btn btn-primary btn-sm">
              <Plus size={16} />
              <span>Create the First Squad</span>
            </button>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {squads.map((squad) => {
              const isFull = squad.member_count >= squad.max_members;

              return (
                <div
                  key={squad.id}
                  className="card"
                  style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}
                >
                  <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '10px' }}>
                    <div>
                      <h4 style={{ fontSize: '1.15rem', fontWeight: 700 }}>{squad.name}</h4>
                      <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '3px' }}>
                        Created for {activeEvent.name}
                      </div>
                    </div>

                    <span className={`badge ${isFull ? 'badge-pink' : 'badge-green'}`}>
                      {squad.member_count} / {squad.max_members} {isFull ? 'Full' : 'Members'}
                    </span>
                  </div>

                  {/* Actions */}
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      flexWrap: 'wrap',
                      gap: '8px',
                      paddingTop: '6px',
                      borderTop: '1px solid rgba(255, 255, 255, 0.06)',
                    }}
                  >
                    <button
                      onClick={() => openSquadDetails(squad.id)}
                      className="btn btn-secondary btn-sm"
                    >
                      <span>View Roster</span>
                    </button>

                    <div style={{ display: 'flex', gap: '8px' }}>
                      {squad.whatsapp_link && (
                        <a
                          href={squad.whatsapp_link}
                          target="_blank"
                          rel="noreferrer"
                          className="btn btn-whatsapp btn-sm"
                          title="Share squad invite on WhatsApp"
                        >
                          <MessageCircle size={15} />
                          <span>Share</span>
                        </a>
                      )}

                      {!isFull ? (
                        <button
                          onClick={() => handleJoinSquad(squad.id)}
                          className="btn btn-primary btn-sm"
                        >
                          <UserPlus size={15} />
                          <span>Join Squad</span>
                        </button>
                      ) : (
                        <span className="badge badge-gray" style={{ alignSelf: 'center' }}>
                          Squad Full
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Create Squad Modal */}
      {isCreateOpen && (
        <div className="modal-overlay" onClick={() => setIsCreateOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Sparkles size={20} color="#f59e0b" />
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Create a Garba Squad</h3>
              </div>
              <button onClick={() => setIsCreateOpen(false)} style={{ color: '#94a3b8' }}>
                <X size={20} />
              </button>
            </div>

            {formError && (
              <div
                style={{
                  background: 'rgba(244, 63, 94, 0.15)',
                  border: '1px solid rgba(244, 63, 94, 0.3)',
                  color: '#fda4af',
                  padding: '10px',
                  borderRadius: '8px',
                  fontSize: '0.85rem',
                  marginBottom: '14px',
                }}
              >
                {formError}
              </div>
            )}

            <form onSubmit={handleCreateSquad} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div className="form-group">
                <label className="form-label">Squad Name *</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Baroda Raas Kings, Dandiya Queens"
                  value={squadName}
                  onChange={(e) => setSquadName(e.target.value)}
                  required
                  maxLength={100}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Max Members (Circle Capacity)</label>
                <select
                  className="form-select"
                  value={maxMembers}
                  onChange={(e) => setMaxMembers(Number(e.target.value))}
                >
                  <option value={4}>4 dancers (Small circle)</option>
                  <option value={6}>6 dancers (Standard circle)</option>
                  <option value={8}>8 dancers (Large circle)</option>
                  <option value={10}>10 dancers (Mega squad)</option>
                </select>
              </div>

              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '10px' }}>
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={() => setIsCreateOpen(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary btn-sm"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Creating...' : 'Create Squad'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Squad Roster Details Modal */}
      {selectedSquad && (
        <div className="modal-overlay" onClick={() => setSelectedSquad(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 800 }}>{selectedSquad.name}</h3>
                <span className="badge badge-gold" style={{ marginTop: '4px' }}>
                  {selectedSquad.member_count} / {selectedSquad.max_members} Members
                </span>
              </div>
              <button onClick={() => setSelectedSquad(null)} style={{ color: '#94a3b8' }}>
                <X size={20} />
              </button>
            </div>

            <div style={{ margin: '16px 0', display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <h4 style={{ fontSize: '0.9rem', color: '#94a3b8', fontWeight: 600 }}>Squad Roster:</h4>
              {selectedSquad.members && selectedSquad.members.length > 0 ? (
                selectedSquad.members.map((m) => (
                  <div
                    key={m.id}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '8px 12px',
                      background: 'rgba(255, 255, 255, 0.04)',
                      borderRadius: '8px',
                    }}
                  >
                    <div>
                      <strong style={{ fontSize: '0.95rem' }}>
                        {m.user?.display_name || 'Attendee'}
                      </strong>
                      <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                        {m.user?.city} {m.user?.instagram_handle && `• ${m.user.instagram_handle}`}
                      </div>
                    </div>

                    {m.user_id === selectedSquad.created_by && (
                      <span className="badge badge-gold">Host</span>
                    )}
                  </div>
                ))
              ) : (
                <p style={{ fontSize: '0.85rem', color: '#64748b' }}>No members yet.</p>
              )}
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '20px' }}>
              {selectedSquad.members?.some((m) => m.user_id === currentUser.id && m.status === 'active') ? (
                <button
                  type="button"
                  onClick={() => handleLeaveSquad(selectedSquad.id)}
                  className="btn btn-danger-outline btn-sm"
                >
                  <LogOut size={14} />
                  <span>Leave Squad</span>
                </button>
              ) : selectedSquad.member_count < selectedSquad.max_members ? (
                <button
                  type="button"
                  onClick={() => handleJoinSquad(selectedSquad.id)}
                  className="btn btn-primary btn-sm"
                >
                  <UserPlus size={15} />
                  <span>Join Squad</span>
                </button>
              ) : (
                <span className="badge badge-pink">Squad Full</span>
              )}

              {selectedSquad.whatsapp_link && (
                <a
                  href={selectedSquad.whatsapp_link}
                  target="_blank"
                  rel="noreferrer"
                  className="btn btn-whatsapp btn-sm"
                >
                  <MessageCircle size={15} />
                  <span>Share on WhatsApp</span>
                </a>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
