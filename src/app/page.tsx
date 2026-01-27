'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getOverviewStats, BugStats } from '@/lib/api';
import PriorityBarChart from '@/components/charts/PriorityBarChart';
import StatusBarChart from '@/components/charts/StatusBarChart';
import TriageTeamChart from '@/components/charts/TriageTeamChart';
import TriageCategoryChart from '@/components/charts/TriageCategoryChart';

export default function Dashboard() {
  const [stats, setStats] = useState<BugStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await getOverviewStats();
        setStats(response.data);
      } catch (err) {
        setError('Failed to load statistics');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
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
            Atlassian Bug Intelligence Dashboard
          </h1>
          <p className="text-gray-600 mt-2">
            Real-time analytics from {stats.total_bugs} bugs
          </p>
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

        {/* AI Triage Insights Section */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <h2 className="text-2xl font-semibold text-gray-900">AI Triage Insights</h2>
            <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">
              {stats.triage_coverage}% coverage
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-xl font-semibold mb-4">Bugs by AI-Suggested Team</h3>
              <TriageTeamChart data={stats.bugs_by_triage_team} />
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-xl font-semibold mb-4">Bugs by AI Category</h3>
              <TriageCategoryChart data={stats.bugs_by_triage_category} />
            </div>
          </div>
        </div>

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