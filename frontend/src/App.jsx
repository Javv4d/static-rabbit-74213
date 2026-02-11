import React, { useEffect, useState } from "react";
import MrrChart from "./components/MrrChart.jsx";
import { fetchMrrData } from "./api.js";

export default function App() {
  const [data, setData] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchMrrData()
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div className="page">
      <header className="header">
        <h1>MRR Dashboard</h1>
        <p>Stripe → BigQuery → React</p>
      </header>
      <section className="card">
        {error ? (
          <div className="error">{error}</div>
        ) : (
          <MrrChart data={data} />
        )}
      </section>
    </div>
  );
}
