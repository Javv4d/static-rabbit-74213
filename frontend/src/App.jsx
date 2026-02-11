import React, { useEffect, useState } from "react";
import MrrChart from "./components/MrrChart.jsx";
import { fetchMrrData } from "./api.js";

export default function App() {
  const [data, setData] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMrrData()
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="page">
      <header className="header">
        <h1>MRR Dashboard</h1>
        <p>Monthly Recurring Revenue Analytics: Stripe → BigQuery → React</p>
      </header>
      <section className="card">
        {loading ? (
          <div className="empty">Loading MRR data...</div>
        ) : error ? (
          <div className="error">Error loading data: {error}</div>
        ) : (
          <MrrChart data={data} />
        )}
      </section>
      <footer style={{ 
        marginTop: '32px', 
        textAlign: 'center', 
        color: '#64748b', 
        fontSize: '14px' 
      }}>
        Data source: BigQuery | Pipeline: Python + SQL | Last updated: {new Date().toLocaleDateString()}
      </footer>
    </div>
  );
}
