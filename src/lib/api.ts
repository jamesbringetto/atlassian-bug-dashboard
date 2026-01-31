import axios from 'axios';

const API_BASE_URL = 'https://atlassian-bug-dashboard-production.up.railway.app/api';

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
  // AI Triage fields
  triage_category: string | null;
  triage_priority: string | null;
  triage_urgency: string | null;
  triage_team: string | null;
  triage_tags: string[] | null;
  triage_confidence: number | null;
  triage_reasoning: string | null;
  triaged_at: string | null;
}

export interface BugStats {
  total_bugs: number;
  open_bugs: number;
  closed_bugs: number;
  avg_resolution_time_days: number | null;
  bugs_by_priority: Record<string, number>;
  bugs_by_status: Record<string, number>;
  recent_activity_count: number;
  // AI Triage aggregations (optional - may not be available if backend isn't updated)
  bugs_by_triage_team?: Record<string, number>;
  bugs_by_triage_category?: Record<string, number>;
  triage_coverage?: number;
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

export const syncBugs = (fetchAll = false, autoTriage = true) =>
  api.post(`/bugs/sync?fetch_all=${fetchAll}&auto_triage=${autoTriage}`);

// Triage endpoints
export const triageBug = (jiraKey: string, force = false) =>
  api.post(`/bugs/${jiraKey}/triage?force=${force}`);

export const getTriageStatus = () =>
  api.get('/bugs/triage/status');

// GitHub/Commit types
export interface Commit {
  id: number;
  sha: string;
  short_sha: string;
  message_headline: string;
  message?: string;
  author_name: string;
  authored_at: string | null;
  url: string;
  jira_keys: string[];
}

export interface GitHubStatus {
  available: boolean;
  repository: string;
  statistics: {
    total_commits: number;
    commits_with_jira_keys: number;
    total_links: number;
    bugs_with_commits: number;
  };
}

// GitHub API functions
export const getCommits = (params?: {
  page?: number;
  page_size?: number;
  jira_key?: string;
}) => api.get<{
  commits: Commit[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}>('/github/commits', { params });

export const getBugCommits = (jiraKey: string) =>
  api.get<{
    jira_key: string;
    commit_count: number;
    commits: Commit[];
  }>(`/bugs/${jiraKey}/commits`);

export const getGitHubStatus = () =>
  api.get<GitHubStatus>('/github/status');