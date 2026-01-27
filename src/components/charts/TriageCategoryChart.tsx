'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface TriageCategoryChartProps {
  data: Record<string, number>;
}

const CATEGORY_LABELS: Record<string, string> = {
  bug: 'Bug',
  feature_request: 'Feature Request',
  documentation: 'Documentation',
  performance: 'Performance',
  security: 'Security',
  ui_ux: 'UI/UX',
  data_issue: 'Data Issue',
  integration: 'Integration',
};

export default function TriageCategoryChart({ data }: TriageCategoryChartProps) {
  const chartData = Object.entries(data)
    .map(([category, count]) => ({
      category: CATEGORY_LABELS[category] || category,
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
        <YAxis dataKey="category" type="category" width={120} />
        <Tooltip />
        <Legend />
        <Bar dataKey="count" fill="#f59e0b" name="Bugs" />
      </BarChart>
    </ResponsiveContainer>
  );
}
