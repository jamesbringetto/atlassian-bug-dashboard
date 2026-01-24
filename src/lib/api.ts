import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Bug types
export interface Bug {
  id: number;
  jira_key: string;
  summary: string;
  status: string;
  priority: string | null;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
  component: string | null;
  reporter: string | null;
  assignee: string | null;
}

export interface BugStats {
  total_bugs: number;
  open_bugs: number;
  closed_bugs: number;
  avg_resolution_time_days: number | null;
  bugs_by_priority: Record<string, number>;
  bugs_by_status: Record<string, number>;
  recent_activity_count: number;
}

// API functions
export const getOverviewStats = () => 
  api.get<BugStats>('/analytics/overview');

export const getBugs = (params?: {
  page?: number;
  page_size?: number;
  status?: string;
  priority?: string;
  search?: string;
}) => api.get('/bugs', { params });

export const getBug = (jiraKey: string) => 
  api.get<Bug>(`/bugs/${jiraKey}`);

export const syncBugs = (fetchAll = false) => 
  api.post(`/bugs/sync?fetch_all=${fetchAll}`);