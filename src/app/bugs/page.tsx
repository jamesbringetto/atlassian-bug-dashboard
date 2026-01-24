'use client';

import { useEffect, useState } from 'react';
import { getBugs } from '@/lib/api';
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
  const pageSize = 25;

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
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Updated</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {bugs.map((bug) => (
                    <tr key={bug.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <a href={'https://jira.atlassian.com/browse/' + bug.jira_key} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800 font-medium">{bug.jira_key}</a>
                      </td>
                      <td className="px-6 py-4"><div className="text-sm text-gray-900 max-w-md truncate">{bug.summary}</div></td>
                      <td className="px-6 py-4"><span className={'px-2 py-1 text-xs font-semibold rounded-full ' + getStatusColor(bug.status)}>{bug.status}</span></td>
                      <td className="px-6 py-4"><span className={'px-2 py-1 text-xs font-semibold rounded-full ' + getPriorityColor(bug.priority)}>{bug.priority || 'None'}</span></td>
                      <td className="px-6 py-4 text-sm text-gray-500">{new Date(bug.updated_at).toLocaleDateString()}</td>
                    </tr>
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