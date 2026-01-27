'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface TriageTeamChartProps {
  data: Record<string, number>;
}

const TEAM_LABELS: Record<string, string> = {
  frontend: 'Frontend',
  backend: 'Backend',
  infrastructure: 'Infrastructure',
  security: 'Security',
  data: 'Data',
  platform: 'Platform',
  mobile: 'Mobile',
  qa: 'QA',
};

export default function TriageTeamChart({ data }: TriageTeamChartProps) {
  const chartData = Object.entries(data)
    .map(([team, count]) => ({
      team: TEAM_LABELS[team] || team,
      count,
    }))
    .sort((a, b) => b.count - a.count);

  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-[300px] text-gray-500">
        No triage data available
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" />
        <YAxis dataKey="team" type="category" width={100} />
        <Tooltip />
        <Legend />
        <Bar dataKey="count" fill="#8b5cf6" name="Bugs" />
      </BarChart>
    </ResponsiveContainer>
  );
}
