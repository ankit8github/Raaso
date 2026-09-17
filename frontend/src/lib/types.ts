export interface User {
  id: string;
  display_name: string;
  age_bracket: string | null;
  city: string;
  instagram_handle: string | null;
  created_at: string;
  updated_at: string;
}

export interface Event {
  id: string;
  name: string;
  city: string;
  venue: string;
  starts_at: string;
  ends_at: string | null;
  ticket_url: string | null;
  is_active: boolean;
  created_at: string;
}

export interface Attendance {
  id: string;
  user_id: string;
  event_id: string;
  intent: string;
  dance_level: string;
  vibes: string | null;
  group_size_preference: number | null;
  created_at: string;
  user?: User;
}

export interface MatchDetail {
  id: string | null;
  attendance_id: string;
  matched_attendance_id: string;
  score: number;
  status: string;
  matched_user: User;
  matched_attendance: Attendance;
  reasons: string[];
  whatsapp_link?: string | null;
}

export interface SquadMember {
  id: string;
  squad_id: string;
  user_id: string;
  status: string;
  joined_at: string;
  user?: User;
}

export interface Squad {
  id: string;
  event_id: string;
  name: string;
  created_by: string;
  max_members: number;
  status: string;
  created_at: string;
  member_count: number;
  whatsapp_link?: string | null;
  creator?: User | null;
  members?: SquadMember[];
}

export interface Report {
  id: string;
  reporter_id: string;
  reported_user_id: string;
  reason: string;
  details?: string | null;
  status: string;
  created_at: string;
}

