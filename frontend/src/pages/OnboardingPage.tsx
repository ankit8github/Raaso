import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Sparkles, ArrowLeft, ArrowRight, Flame } from 'lucide-react';
import { api } from '../api/client';
import type { Event } from '../lib/types';

const INTENTS = [
  { id: 'hardcore_garba', label: 'Hardcore Garba', desc: 'Non-stop rounds, high stamina & fast steps' },
  { id: 'social_casual', label: 'Social & Casual', desc: 'Fun dancing, making friends & festive energy' },
  { id: 'chilling_food', label: 'Chilling & Food', desc: 'Music vibes, food stalls, photos & casual grooving' },
  { id: 'learning', label: 'Learning & Practicing', desc: 'Beginner friendly circles to pick up the steps' },
];

const DANCE_LEVELS = [
  { id: 'beginner', label: 'Beginner', desc: 'Basic steps (2-taali, simple 3-taali)' },
  { id: 'intermediate', label: 'Intermediate', desc: 'Comfortable with rhythm, spins & rounds' },
  { id: 'pro', label: 'Pro / Advanced', desc: 'Fast dodhiya, complex choreography & non-stop energy' },
];

const AVAILABLE_VIBES = [
  'traditional',
  'bollywood',
  'fast_paced',
  'late_night',
  'photogenic',
  'high_energy',
  'relaxed',
  'food_focused',
  'family_friendly',
];

export const OnboardingPage: React.FC = () => {
  const { eventId } = useParams<{ eventId: string }>();
  const navigate = useNavigate();

  const [event, setEvent] = useState<Event | null>(null);
  const [displayName, setDisplayName] = useState('');
  const [ageBracket, setAgeBracket] = useState('21-25');
  const [city, setCity] = useState('');
  const [instagramHandle, setInstagramHandle] = useState('');
  const [intent, setIntent] = useState('hardcore_garba');
  const [danceLevel, setDanceLevel] = useState('intermediate');
  const [selectedVibes, setSelectedVibes] = useState<string[]>(['traditional', 'high_energy']);
  const [groupSize, setGroupSize] = useState<number>(6);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadEvent() {
      if (!eventId) return;
      try {
        const data = await api.getEvent(eventId);
        setEvent(data);
        if (!city) setCity(data.city);
      } catch (err: any) {
        setError(err.message || 'Failed to load event details.');
      }
    }

    // Prepopulate existing user profile if in localStorage
    const savedUser = localStorage.getItem('raaso_user');
    if (savedUser) {
      try {
        const u = JSON.parse(savedUser);
        if (u.display_name) setDisplayName(u.display_name);
        if (u.age_bracket) setAgeBracket(u.age_bracket);
        if (u.city) setCity(u.city);
        if (u.instagram_handle) setInstagramHandle(u.instagram_handle);
      } catch {
        // ignore
      }
    }

    loadEvent();
  }, [eventId]);

  const toggleVibe = (vibe: string) => {
    if (selectedVibes.includes(vibe)) {
      setSelectedVibes(selectedVibes.filter((v) => v !== vibe));
    } else {
      setSelectedVibes([...selectedVibes, vibe]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!eventId) return;
    if (!displayName.trim()) {
      setError('Please provide your name or display nickname.');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      // 1. Create or load user
      const user = await api.createUser({
        display_name: displayName.trim(),
        age_bracket: ageBracket,
        city: city.trim() || (event ? event.city : 'Gujarat'),
        instagram_handle: instagramHandle.trim() || null,
      });

      localStorage.setItem('raaso_user', JSON.stringify(user));

      // 2. Create attendance
      let attendance;
      try {
        attendance = await api.createAttendance({
          user_id: user.id,
          event_id: eventId,
          intent,
          dance_level: danceLevel,
          vibes: selectedVibes.join(', '),
          group_size_preference: groupSize,
        });
      } catch (attErr: any) {
        // If user already registered attendance for this event, fetch user attendances
        if (attErr.message && attErr.message.includes('already exists')) {
          const res = await fetch(`/api/attendances/user/${user.id}`);
          const list = await res.json();
          const match = list.find((a: any) => a.event_id === eventId);
          if (match) {
            attendance = match;
          } else {
            throw attErr;
          }
        } else {
          throw attErr;
        }
      }

      localStorage.setItem('raaso_attendance_id', attendance.id);
      localStorage.setItem('raaso_event_id', eventId);
      if (event) {
        localStorage.setItem('raaso_active_event', JSON.stringify(event));
      }

      // 3. Navigate to matches
      navigate('/matches');
    } catch (err: any) {
      setError(err.message || 'Failed to submit profile. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <button
        type="button"
        onClick={() => navigate('/')}
        className="btn btn-secondary btn-sm"
        style={{ width: 'fit-content' }}
      >
        <ArrowLeft size={16} />
        <span>Back to Events</span>
      </button>

      {event && (
        <div
          className="card"
          style={{
            background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(244, 63, 94, 0.1))',
            border: '1px solid rgba(245, 158, 11, 0.3)',
          }}
        >
          <span className="badge badge-gold" style={{ marginBottom: '6px' }}>
            Event Attendance Profile
          </span>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 800 }}>{event.name}</h2>
          <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
            📍 {event.venue}, {event.city}
          </p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '4px' }}>
            1. Your Festival Profile
          </h3>
          <p style={{ fontSize: '0.82rem', color: '#94a3b8' }}>
            Only your display name and dance preferences are visible to fellow attendees.
          </p>
        </div>

        {error && (
          <div
            style={{
              background: 'rgba(244, 63, 94, 0.15)',
              border: '1px solid rgba(244, 63, 94, 0.3)',
              color: '#fda4af',
              padding: '12px',
              borderRadius: '8px',
              fontSize: '0.88rem',
            }}
          >
            {error}
          </div>
        )}

        <div className="form-group">
          <label className="form-label">Display Name / Nickname *</label>
          <input
            type="text"
            className="form-input"
            placeholder="e.g. Diya P."
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            required
            maxLength={100}
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
          <div className="form-group">
            <label className="form-label">Age Bracket</label>
            <select
              className="form-select"
              value={ageBracket}
              onChange={(e) => setAgeBracket(e.target.value)}
            >
              <option value="18-20">18 - 20</option>
              <option value="21-25">21 - 25</option>
              <option value="26-30">26 - 30</option>
              <option value="31+">31+</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">City</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Vadodara"
              value={city}
              onChange={(e) => setCity(e.target.value)}
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Instagram Handle (Optional)</label>
          <input
            type="text"
            className="form-input"
            placeholder="e.g. @diya_garba (for social discovery)"
            value={instagramHandle}
            onChange={(e) => setInstagramHandle(e.target.value)}
          />
          <div className="form-hint">
            We never ask for or share your private phone number or email address.
          </div>
        </div>

        <hr style={{ borderColor: 'rgba(255, 255, 255, 0.08)' }} />

        <div>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '4px' }}>
            2. Dance Intent & Energy
          </h3>
          <p style={{ fontSize: '0.82rem', color: '#94a3b8' }}>
            How do you plan on spending the night?
          </p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {INTENTS.map((item) => (
            <div
              key={item.id}
              onClick={() => setIntent(item.id)}
              style={{
                border: `1px solid ${intent === item.id ? '#f59e0b' : 'rgba(255, 255, 255, 0.1)'}`,
                background: intent === item.id ? 'rgba(245, 158, 11, 0.12)' : 'var(--bg-input)',
                padding: '14px',
                borderRadius: '12px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <strong style={{ fontSize: '0.95rem', color: intent === item.id ? '#fbbf24' : '#fff' }}>
                  {item.label}
                </strong>
                {intent === item.id && <Flame size={18} color="#f59e0b" />}
              </div>
              <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '4px' }}>
                {item.desc}
              </p>
            </div>
          ))}
        </div>

        <div>
          <label className="form-label" style={{ marginBottom: '8px' }}>Dance Skill Level</label>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '10px' }}>
            {DANCE_LEVELS.map((item) => (
              <div
                key={item.id}
                onClick={() => setDanceLevel(item.id)}
                style={{
                  border: `1px solid ${danceLevel === item.id ? '#f43f5e' : 'rgba(255, 255, 255, 0.1)'}`,
                  background: danceLevel === item.id ? 'rgba(244, 63, 94, 0.12)' : 'var(--bg-input)',
                  padding: '12px',
                  borderRadius: '10px',
                  cursor: 'pointer',
                  textAlign: 'center',
                }}
              >
                <div style={{ fontWeight: 700, fontSize: '0.9rem', color: danceLevel === item.id ? '#fda4af' : '#fff' }}>
                  {item.label}
                </div>
                <div style={{ fontSize: '0.72rem', color: '#94a3b8', marginTop: '4px' }}>
                  {item.desc}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <label className="form-label" style={{ marginBottom: '8px' }}>Vibes (Pick all that apply)</label>
          <div className="tag-chips">
            {AVAILABLE_VIBES.map((vibe) => {
              const isSelected = selectedVibes.includes(vibe);
              return (
                <button
                  type="button"
                  key={vibe}
                  className={`chip-btn ${isSelected ? 'selected' : ''}`}
                  onClick={() => toggleVibe(vibe)}
                >
                  {vibe.replace('_', ' ')}
                </button>
              );
            })}
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Ideal Squad Size Preference</label>
          <div style={{ display: 'flex', gap: '10px' }}>
            {[2, 4, 6, 8].map((size) => (
              <button
                type="button"
                key={size}
                className={`chip-btn ${groupSize === size ? 'selected' : ''}`}
                style={{ flex: 1, textAlign: 'center', padding: '10px 0' }}
                onClick={() => setGroupSize(size)}
              >
                {size} dancers
              </button>
            ))}
          </div>
        </div>

        <button
          type="submit"
          className="btn btn-primary"
          style={{ width: '100%', marginTop: '10px' }}
          disabled={isSubmitting}
        >
          {isSubmitting ? (
            <div className="spinner" style={{ width: '20px', height: '20px' }} />
          ) : (
            <>
              <Sparkles size={18} />
              <span>Find Compatible Matches & Squads</span>
              <ArrowRight size={18} />
            </>
          )}
        </button>
      </form>
    </div>
  );
};
