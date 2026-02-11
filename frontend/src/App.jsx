import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  const [mrrData, setMrrData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Load MRR data from JSON file
    fetch('/data/mrr_metrics.json')
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to load MRR data');
        }
        return response.json();
      })
      .then(data => {
        setMrrData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error loading MRR data:', err);
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading MRR Analytics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <h2>Error Loading Data</h2>
        <p>{error}</p>
        <p className="error-hint">
          Make sure to run the data generator and ETL scripts first:
        </p>
        <pre>
          python scripts/generate_data.py{'\n'}
          python scripts/etl_pipeline.py
        </pre>
      </div>
    );
  }

  return (
    <div className="App">
      <Dashboard data={mrrData} />
    </div>
  );
}

export default App;
