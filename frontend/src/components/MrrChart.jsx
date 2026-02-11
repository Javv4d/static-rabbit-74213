import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from "recharts";

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{
        background: '#fff',
        padding: '12px 16px',
        border: '1px solid #e2e8f0',
        borderRadius: '8px',
        boxShadow: '0 4px 12px rgba(15, 23, 42, 0.1)'
      }}>
        <p style={{ margin: '0 0 4px', fontWeight: 600, color: '#0f172a' }}>
          {payload[0].payload.month}
        </p>
        <p style={{ margin: 0, color: '#2563eb', fontWeight: 500 }}>
          MRR: ${payload[0].value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </p>
      </div>
    );
  }
  return null;
};

export default function MrrChart({ data }) {
  if (!data || data.length === 0) {
    return <div className="empty">No MRR data yet. Run the ETL pipeline to populate data.</div>;
  }

  return (
    <div className="chart">
      <h2 style={{ margin: '0 0 24px', fontSize: '20px', fontWeight: 600, color: '#0f172a' }}>
        Monthly Recurring Revenue Trend
      </h2>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={data} margin={{ top: 10, right: 30, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis 
            dataKey="month" 
            stroke="#64748b"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="#64748b"
            style={{ fontSize: '12px' }}
            tickFormatter={(value) => `$${value.toLocaleString()}`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="line"
          />
          <Line 
            type="monotone" 
            dataKey="mrr_amount" 
            stroke="#2563eb" 
            strokeWidth={3}
            dot={{ fill: '#2563eb', r: 5 }}
            activeDot={{ r: 7 }}
            name="MRR Amount (USD)"
          />
        </LineChart>
      </ResponsiveContainer>
      <div style={{ 
        marginTop: '24px', 
        padding: '16px', 
        background: '#f8fafc', 
        borderRadius: '8px',
        fontSize: '14px',
        color: '#64748b'
      }}>
        <strong style={{ color: '#0f172a' }}>Total Months:</strong> {data.length} | {' '}
        <strong style={{ color: '#0f172a' }}>Latest MRR:</strong> ${data[data.length - 1]?.mrr_amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
      </div>
    </div>
  );
}
