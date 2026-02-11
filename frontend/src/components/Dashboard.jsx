import React from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart
} from 'recharts';
import './Dashboard.css';

const Dashboard = ({ data }) => {
  // Calculate summary metrics
  const latestMonth = data[data.length - 1] || {};
  const previousMonth = data[data.length - 2] || {};
  
  const calculateChange = (current, previous) => {
    if (!previous || previous === 0) return 0;
    return ((current - previous) / previous * 100).toFixed(1);
  };

  const mrrChange = calculateChange(latestMonth.total_mrr, previousMonth.total_mrr);
  const customerChange = calculateChange(latestMonth.active_customers, previousMonth.active_customers);

  // Format currency
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="label">{`Month: ${label}`}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }}>
              {`${entry.name}: ${entry.name.includes('MRR') || entry.name.includes('mrr') ? formatCurrency(entry.value) : entry.value}`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>MRR Analytics Dashboard</h1>
        <p className="subtitle">Monthly Recurring Revenue Insights</p>
      </header>

      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">💰</div>
          <div className="metric-content">
            <h3>Total MRR</h3>
            <div className="metric-value">{formatCurrency(latestMonth.total_mrr || 0)}</div>
            <div className={`metric-change ${mrrChange >= 0 ? 'positive' : 'negative'}`}>
              {mrrChange >= 0 ? '↑' : '↓'} {Math.abs(mrrChange)}% from last month
            </div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">👥</div>
          <div className="metric-content">
            <h3>Active Customers</h3>
            <div className="metric-value">{latestMonth.active_customers || 0}</div>
            <div className={`metric-change ${customerChange >= 0 ? 'positive' : 'negative'}`}>
              {customerChange >= 0 ? '↑' : '↓'} {Math.abs(customerChange)}% from last month
            </div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">📈</div>
          <div className="metric-content">
            <h3>New MRR</h3>
            <div className="metric-value">{formatCurrency(latestMonth.new_mrr || 0)}</div>
            <div className="metric-info">This month's new subscriptions</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">📉</div>
          <div className="metric-content">
            <h3>Churn MRR</h3>
            <div className="metric-value">{formatCurrency(latestMonth.churn_mrr || 0)}</div>
            <div className="metric-info">Lost revenue this month</div>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h2>MRR Trend</h2>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={data}>
              <defs>
                <linearGradient id="colorMrr" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#667eea" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#667eea" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis dataKey="month" stroke="#666" />
              <YAxis stroke="#666" tickFormatter={(value) => `$${value}`} />
              <Tooltip content={<CustomTooltip />} />
              <Area 
                type="monotone" 
                dataKey="total_mrr" 
                stroke="#667eea" 
                fillOpacity={1} 
                fill="url(#colorMrr)"
                name="Total MRR"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h2>Active Customers</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis dataKey="month" stroke="#666" />
              <YAxis stroke="#666" />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="active_customers" 
                stroke="#10b981" 
                strokeWidth={2}
                dot={{ fill: '#10b981', r: 4 }}
                name="Active Customers"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card full-width">
          <h2>MRR Breakdown</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis dataKey="month" stroke="#666" />
              <YAxis stroke="#666" tickFormatter={(value) => `$${value}`} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Bar dataKey="new_mrr" fill="#10b981" name="New MRR" />
              <Bar dataKey="expansion_mrr" fill="#3b82f6" name="Expansion MRR" />
              <Bar dataKey="contraction_mrr" fill="#f59e0b" name="Contraction MRR" />
              <Bar dataKey="churn_mrr" fill="#ef4444" name="Churn MRR" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card full-width">
          <h2>Customer Growth</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis dataKey="month" stroke="#666" />
              <YAxis stroke="#666" />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Bar dataKey="new_customers" fill="#10b981" name="New Customers" />
              <Bar dataKey="churned_customers" fill="#ef4444" name="Churned Customers" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <footer className="dashboard-footer">
        <p>Data updated: {latestMonth.month || 'N/A'}</p>
      </footer>
    </div>
  );
};

export default Dashboard;
