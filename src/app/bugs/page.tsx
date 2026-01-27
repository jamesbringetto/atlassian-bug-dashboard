'use client';

import { useEffect, useState } from 'react';
import { getBugs, triageBug } from '@/lib/api';
import Link from 'next/link';

interface Bug {
  id: number;
  jira_key: string;
  summary: string;
  status: string;
  priority: string | null;
  created_at: string;
  updated_at: string;
  component: string | null;
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

export default function BugsPage() {
  const [bugs, setBugs] = useState<Bug[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [expandedBug, setExpandedBug] = useState<string | null>(null);
  const [triaging, setTriaging] = useState<string | null>(null);
  const pageSize = 25;

  const handleTriage = async (jiraKey: string) => {
    setTriaging(jiraKey);
    try {
      await triageBug(jiraKey, true);
      // Refresh bugs to get updated triage data
      const response = await getBugs({
        page,
        page_size: pageSize,
        search: searchTerm || undefined,
        status: statusFilter || undefined,
        priority: priorityFilter || undefined,
      });
      setBugs(response.data.bugs);
    } catch (err) {
      console.error('Triage failed:', err);
    } finally {
      setTriaging(null);
    }
  };

  const getTriageUrgencyColor = (urgency: string | null) => {
    if (urgency === 'immediate') return 'bg-red-100 text-red-800 border-red-200';
    if (urgency === 'soon') return 'bg-orange-100 text-orange-800 border-orange-200';
    if (urgency === 'normal') return 'bg-blue-100 text-blue-800 border-blue-200';
    if (urgency === 'backlog') return 'bg-gray-100 text-gray-600 border-gray-200';
    return 'bg-gray-50 text-gray-500 border-gray-200';
  };

  const getTriageCategoryIcon = (category: string | null) => {
    const icons: Record<string, string> = {
      'bug': '\uD83D\uDC1B',
      'security': '\uD83D\uDD12',
      'performance': '\u26A1',
      'feature_request': '\u2728',
      'documentation': '\uD83D\uDCDD',
      'ui_ux': '\uD83C\uDFA8',
      'data_issue': '\uD83D\uDCCA',
      'integration': '\uD83D\uDD17',
    };
    return icons[category || ''] || '\uD83D\uDD0D';
  };

  useEffect(() => {
    const fetchBugs = async () => {
      setLoading(true);
      try {
        const response = await getBugs({
          page,
          page_size: pageSize,
          search: searchTerm || undefined,
          status: statusFilter || undefined,
          priority: priorityFilter || undefined,
        });
        setBugs(response.data.bugs);
        setTotal(response.data.total);
      } catch (err) {
        setError('Failed to load bugs');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchBugs();
  }, [page, searchTerm, statusFilter, priorityFilter]);

  const totalPages = Math.ceil(total / pageSize);

  const getPriorityColor = (priority: string | null) => {
    if (priority === 'High') return 'bg-red-100 text-red-800';
    if (priority === 'Medium') return 'bg-yellow-100 text-yellow-800';
    if (priority === 'Low') return 'bg-green-100 text-green-800';
    return 'bg-gray-100 text-gray-800';
  };

  const getStatusColor = (status: string) => {
    if (status.includes('Progress')) return 'bg-blue-100 text-blue-800';
    if (status.includes('Review')) return 'bg-purple-100 text-purple-800';
    if (status.includes('Backlog')) return 'bg-gray-100 text-gray-800';
    return 'bg-slate-100 text-slate-800';
  };

  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <Link href="/" className="text-blue-600 hover:text-blue-800 mb-2 inline-block">
            ← Back to Dashboard
          </Link>
          <h1 className="text-4xl font-bold text-gray-900">Bug List</h1>
          <p className="text-gray-600 mt-2">{total} total bugs</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
              <input
                type="text"
                placeholder="Search in summary..."
                value={searchTerm}
                onChange={(e) => { setSearchTerm(e.target.value); setPage(1); }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
              <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }} className="w-full px-4 py-2 border border-gray-300 rounded-lg">
                <option value="">All Statuses</option>
                <option value="Gathering Impact">Gathering Impact</option>
                <option value="Short Term Backlog">Short Term Backlog</option>
                <option value="In Progress">In Progress</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Priority</label>
              <select value={priorityFilter} onChange={(e) => { setPriorityFilter(e.target.value); setPage(1); }} className="w-full px-4 py-2 border border-gray-300 rounded-lg">
                <option value="">All Priorities</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow overflow-hidden">
          {loading ? (
            <div className="p-8 text-center">Loading...</div>
          ) : error ? (
            <div className="p-8 text-center text-red-500">{error}</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Key</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Summary</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Priority</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">AI Triage</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Updated</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {bugs.map((bug) => (
                    <>
                      <tr key={bug.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => setExpandedBug(expandedBug === bug.jira_key ? null : bug.jira_key)}>
                        <td className="px-6 py-4">
                          <a href={'https://jira.atlassian.com/browse/' + bug.jira_key} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800 font-medium" onClick={(e) => e.stopPropagation()}>{bug.jira_key}</a>
                        </td>
                        <td className="px-6 py-4"><div className="text-sm text-gray-900 max-w-md truncate">{bug.summary}</div></td>
                        <td className="px-6 py-4"><span className={'px-2 py-1 text-xs font-semibold rounded-full ' + getStatusColor(bug.status)}>{bug.status}</span></td>
                        <td className="px-6 py-4"><span className={'px-2 py-1 text-xs font-semibold rounded-full ' + getPriorityColor(bug.priority)}>{bug.priority || 'None'}</span></td>
                        <td className="px-6 py-4">
                          {bug.triaged_at ? (
                            <div className="flex items-center gap-2">
                              <span className="text-lg" title={bug.triage_category || 'Unknown'}>{getTriageCategoryIcon(bug.triage_category)}</span>
                              <span className={'px-2 py-1 text-xs font-medium rounded border ' + getTriageUrgencyColor(bug.triage_urgency)}>
                                {bug.triage_urgency || 'N/A'}
                              </span>
                              {bug.triage_team && (
                                <span className="px-2 py-1 text-xs bg-indigo-50 text-indigo-700 rounded">
                                  {bug.triage_team}
                                </span>
                              )}
                            </div>
                          ) : (
                            <button
                              onClick={(e) => { e.stopPropagation(); handleTriage(bug.jira_key); }}
                              disabled={triaging === bug.jira_key}
                              className="px-2 py-1 text-xs bg-purple-100 text-purple-700 rounded hover:bg-purple-200 disabled:opacity-50"
                            >
                              {triaging === bug.jira_key ? 'Triaging...' : 'Triage'}
                            </button>
                          )}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">{new Date(bug.updated_at).toLocaleDateString()}</td>
                      </tr>
                      {expandedBug === bug.jira_key && bug.triaged_at && (
                        <tr key={`${bug.id}-expanded`} className="bg-gray-50">
                          <td colSpan={6} className="px-6 py-4">
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                              <div>
                                <span className="font-medium text-gray-500">Category:</span>
                                <p className="text-gray-900 capitalize">{bug.triage_category || 'N/A'}</p>
                              </div>
                              <div>
                                <span className="font-medium text-gray-500">AI Priority:</span>
                                <p className="text-gray-900 capitalize">{bug.triage_priority || 'N/A'}</p>
                              </div>
                              <div>
                                <span className="font-medium text-gray-500">Team:</span>
                                <p className="text-gray-900 capitalize">{bug.triage_team || 'N/A'}</p>
                              </div>
                              <div>
                                <span className="font-medium text-gray-500">Confidence:</span>
                                <p className="text-gray-900">{bug.triage_confidence ? `${Math.round(bug.triage_confidence * 100)}%` : 'N/A'}</p>
                              </div>
                              <div className="col-span-2 md:col-span-4">
                                <span className="font-medium text-gray-500">AI Reasoning:</span>
                                <p className="text-gray-700 mt-1">{bug.triage_reasoning || 'No reasoning provided'}</p>
                              </div>
                              {bug.triage_tags && bug.triage_tags.length > 0 && (
                                <div className="col-span-2 md:col-span-4">
                                  <span className="font-medium text-gray-500">Tags:</span>
                                  <div className="flex flex-wrap gap-1 mt-1">
                                    {bug.triage_tags.map((tag, i) => (
                                      <span key={i} className="px-2 py-0.5 text-xs bg-gray-200 text-gray-700 rounded">{tag}</span>
                                    ))}
                                  </div>
                                </div>
                              )}
                              <div className="col-span-2 md:col-span-4 flex justify-end">
                                <button
                                  onClick={(e) => { e.stopPropagation(); handleTriage(bug.jira_key); }}
                                  disabled={triaging === bug.jira_key}
                                  className="px-3 py-1 text-xs bg-purple-100 text-purple-700 rounded hover:bg-purple-200 disabled:opacity-50"
                                >
                                  {triaging === bug.jira_key ? 'Re-triaging...' : 'Re-triage'}
                                </button>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </>
                  ))}
                </tbody>
              </table>
              <div className="px-6 py-4 border-t flex items-center justify-between">
                <p className="text-sm text-gray-700">Page {page} of {totalPages} ({total} total)</p>
                <div className="flex gap-2">
                  <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="px-4 py-2 border rounded-lg disabled:opacity-50 hover:bg-gray-50">Previous</button>
                  <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages} className="px-4 py-2 border rounded-lg disabled:opacity-50 hover:bg-gray-50">Next</button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}