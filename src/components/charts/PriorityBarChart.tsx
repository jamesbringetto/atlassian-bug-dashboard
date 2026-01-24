'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface PriorityBarChartProps {
  data: Record<string, number>;
}

export default function PriorityBarChart({ data }: PriorityBarChartProps) {
  // Transform data for recharts
  const chartData = Object.entries(data).map(([priority, count]) => ({
    priority,
    count,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="priority" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="count" fill="#3b82f6" name="Bugs" />
      </BarChart>
    </ResponsiveContainer>
  );
}