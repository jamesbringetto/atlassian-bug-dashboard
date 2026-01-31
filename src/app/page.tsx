'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getOverviewStats, getCommits, BugStats, Commit } from '@/lib/api';
import PriorityBarChart from '@/components/charts/PriorityBarChart';
import StatusBarChart from '@/components/charts/StatusBarChart';
import TriageTeamChart from '@/components/charts/TriageTeamChart';
import TriageCategoryChart from '@/components/charts/TriageCategoryChart';

export default function Dashboard() {
  const [stats, setStats] = useState<BugStats | null>(null);
  const [commits, setCommits] = useState<Commit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsResponse, commitsResponse] = await Promise.all([
          getOverviewStats(),
          getCommits({ page: 1, page_size: 5 }).catch(() => null)
        ]);
        setStats(statsResponse.data);
        if (commitsResponse) {
          setCommits(commitsResponse.data.commits);
        }
      } catch (err) {
        setError('Failed to load statistics');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-red-500">{error || 'No data available'}</div>
      </div>
    );
  }

  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">
            Atlassian Cloud Migration Bug Intelligence Dashboard
          </h1>
          <p className="text-gray-600 mt-2">
            Real-time analytics and AI-powered triage for Atlassian cloud migration bugs
          </p>
          <p className="text-gray-500 text-sm mt-1">
            Tracking {stats.total_bugs} bugs · Updated daily · Last refresh: {new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
          </p>
          <div className="flex items-center gap-4 mt-3 text-sm">
            <a
              href="https://www.linkedin.com/in/jamesbringetto/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 hover:underline"
            >
              Built by James Bringetto · Connect on LinkedIn
            </a>
            <span className="text-gray-300">|</span>
            <a
              href="https://github.com/jamesbringetto/atlassian-bug-dashboard"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-600 hover:text-gray-800 hover:underline"
            >
              View on GitHub
            </a>
          </div>
          <Link
            href="/bugs"
            className="inline-block mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            View All Bugs →
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatCard title="Total Bugs" value={stats.total_bugs} color="blue" />
          <StatCard title="Open Bugs" value={stats.open_bugs} color="yellow" />
          <StatCard title="Closed Bugs" value={stats.closed_bugs} color="green" />
          <StatCard 
            title="Avg Resolution Time" 
            value={stats.avg_resolution_time_days ? `${stats.avg_resolution_time_days} days` : 'N/A'} 
            color="purple" 
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Bugs by Priority</h2>
            <PriorityBarChart data={stats.bugs_by_priority} />
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Bugs by Status</h2>
            <StatusBarChart data={stats.bugs_by_status} />
          </div>
        </div>

        {/* AI Triage Insights Section - only show if triage data is available */}
        {(stats.bugs_by_triage_team || stats.bugs_by_triage_category) && (
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-4">
              <h2 className="text-2xl font-semibold text-gray-900">AI Triage Insights</h2>
              {stats.triage_coverage !== undefined && (
                <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">
                  {stats.triage_coverage}% coverage
                </span>
              )}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-xl font-semibold mb-4">Bugs by AI-Suggested Team</h3>
                <TriageTeamChart data={stats.bugs_by_triage_team || {}} />
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-xl font-semibold mb-4">Bugs by AI Category</h3>
                <TriageCategoryChart data={stats.bugs_by_triage_category || {}} />
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Priority Breakdown</h2>
            <div className="space-y-3">
              {Object.entries(stats.bugs_by_priority).sort((a, b) => b[1] - a[1]).map(([priority, count]) => (
                <div key={priority} className="flex justify-between items-center">
                  <span className="text-gray-700">{priority}</span>
                  <span className="font-semibold text-gray-900">{count}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Status Breakdown</h2>
            <div className="space-y-3">
              {Object.entries(stats.bugs_by_status).sort((a, b) => b[1] - a[1]).map(([status, count]) => (
                <div key={status} className="flex justify-between items-center">
                  <span className="text-gray-700">{status}</span>
                  <span className="font-semibold text-gray-900">{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-6 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-2">Recent Activity</h2>
          <p className="text-gray-600">
            {stats.recent_activity_count} bugs updated in the last 7 days
          </p>
        </div>

        {/* Recent Commits Section */}
        {commits.length > 0 && (
          <div className="mt-6 bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Recent Commits</h2>
              <Link
                href="/commits"
                className="text-blue-600 hover:text-blue-800 text-sm"
              >
                View all commits →
              </Link>
            </div>
            <div className="space-y-3">
              {commits.map((commit) => (
                <div key={commit.sha} className="border-b border-gray-100 pb-3 last:border-0">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <a
                        href={commit.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 font-mono text-sm"
                      >
                        {commit.short_sha}
                      </a>
                      <span className="mx-2 text-gray-300">·</span>
                      <span className="text-gray-900 text-sm truncate">{commit.message_headline}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-gray-500 text-xs">{commit.author_name}</span>
                    {commit.authored_at && (
                      <>
                        <span className="text-gray-300">·</span>
                        <span className="text-gray-500 text-xs">
                          {new Date(commit.authored_at).toLocaleDateString()}
                        </span>
                      </>
                    )}
                    {commit.jira_keys.length > 0 && (
                      <>
                        <span className="text-gray-300">·</span>
                        <div className="flex gap-1">
                          {commit.jira_keys.map((key) => (
                            <a
                              key={key}
                              href={`https://jira.atlassian.com/browse/${key}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="px-1.5 py-0.5 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                            >
                              {key}
                            </a>
                          ))}
                        </div>
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}

function StatCard({ title, value, color }: { title: string; value: string | number; color: 'blue' | 'yellow' | 'green' | 'purple' }) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-700 border-blue-200',
    yellow: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    green: 'bg-green-50 text-green-700 border-green-200',
    purple: 'bg-purple-50 text-purple-700 border-purple-200',
  };

  return (
    <div className={`rounded-lg border-2 p-6 ${colorClasses[color]}`}>
      <div className="text-sm font-medium opacity-80">{title}</div>
      <div className="text-3xl font-bold mt-2">{value}</div>
    </div>
  );
}