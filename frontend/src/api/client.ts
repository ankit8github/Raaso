import type { Attendance, Event, MatchDetail, Report, Squad, User } from '../lib/types';

const API_BASE = '/api';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = `Request failed: ${res.statusText}`;
    try {
      const errJson = await res.json();
      if (errJson.detail) {
        errorDetail = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
      }
    } catch {
      // ignore
    }
    throw new Error(errorDetail);
  }
  return res.json();
}

export const api = {
  async getEvents(city?: string): Promise<Event[]> {
    const url = new URL(`${window.location.origin}${API_BASE}/events`);
    if (city) url.searchParams.append('city', city);
    const res = await fetch(url.toString());
    return handleResponse<Event[]>(res);
  },

  async getEvent(id: string): Promise<Event> {
    const res = await fetch(`${API_BASE}/events/${id}`);
    return handleResponse<Event>(res);
  },

  async createUser(payload: {
    display_name: string;
    age_bracket?: string | null;
    city: string;
    instagram_handle?: string | null;
  }): Promise<User> {
    const res = await fetch(`${API_BASE}/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<User>(res);
  },

  async getUser(id: string): Promise<User> {
    const res = await fetch(`${API_BASE}/users/${id}`);
    return handleResponse<User>(res);
  },

  async createAttendance(payload: {
    user_id: string;
    event_id: string;
    intent: string;
    dance_level: string;
    vibes?: string | null;
    group_size_preference?: number | null;
  }): Promise<Attendance> {
    const res = await fetch(`${API_BASE}/attendances`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<Attendance>(res);
  },

  async getAttendance(id: string): Promise<Attendance> {
    const res = await fetch(`${API_BASE}/attendances/${id}`);
    return handleResponse<Attendance>(res);
  },

  async getMatches(attendanceId: string): Promise<MatchDetail[]> {
    const res = await fetch(`${API_BASE}/attendances/${attendanceId}/matches`);
    return handleResponse<MatchDetail[]>(res);
  },

  async getSquads(eventId: string): Promise<Squad[]> {
    const res = await fetch(`${API_BASE}/squads/event/${eventId}`);
    return handleResponse<Squad[]>(res);
  },

  async getSquad(squadId: string): Promise<Squad> {
    const res = await fetch(`${API_BASE}/squads/${squadId}`);
    return handleResponse<Squad>(res);
  },

  async createSquad(payload: {
    event_id: string;
    created_by: string;
    name: string;
    max_members?: number;
  }): Promise<Squad> {
    const res = await fetch(`${API_BASE}/squads`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<Squad>(res);
  },

  async joinSquad(squadId: string, userId: string): Promise<Squad> {
    const res = await fetch(`${API_BASE}/squads/${squadId}/join`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId }),
    });
    return handleResponse<Squad>(res);
  },

  async leaveSquad(squadId: string, userId: string): Promise<{ status: string; message: string }> {
    const res = await fetch(`${API_BASE}/squads/${squadId}/leave`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId }),
    });
    return handleResponse<{ status: string; message: string }>(res);
  },

  async submitReport(payload: {
    reporter_id: string;
    reported_user_id: string;
    reason: string;
    details?: string | null;
  }): Promise<Report> {
    const res = await fetch(`${API_BASE}/reports`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<Report>(res);
  },
};

