'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface StatusBarChartProps {
  data: Record<string, number>;
}

export default function StatusBarChart({ data }: StatusBarChartProps) {
  // Transform and sort data by count
  const chartData = Object.entries(data)
    .map(([status, count]) => ({
      status: status.length > 20 ? status.substring(0, 20) + '...' : status,
      fullStatus: status,
      count,
    }))
    .sort((a, b) => b.count - a.count);

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" />
        <YAxis dataKey="status" type="category" width={150} />
        <Tooltip />
        <Legend />
        <Bar dataKey="count" fill="#10b981" name="Bugs" />
      </BarChart>
    </ResponsiveContainer>
  );
}