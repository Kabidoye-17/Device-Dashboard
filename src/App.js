import React, { useState, useEffect } from 'react';
import { apiUrl } from './config';

function App() {
  const [metrics, setMetrics] = useState({
    cpu_load: 0,
    ram_usage: 0,
    network_sent: 0,
    timestamp: '-'
  });
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch(`${apiUrl}/system-metrics`);
        const data = await response.json();
        setMetrics(data);
        setError(null);
      } catch (error) {
        console.error('Error:', error);
        setError(error.message);
      }
    };

    fetchMetrics();
  }, []);

  return (
    <div>
      {error ? (
        <p>Error: {error}</p>
      ) : (
        <div>
          <p>CPU Load: {metrics.cpu_load}%</p>
          <p>RAM Usage: {metrics.ram_usage}%</p>
          <p>Network Data Sent: {metrics.network_sent} MB (since boot)</p>
          <p>Last Updated: {metrics.timestamp}</p>
        </div>
      )}
    </div>
  );
}

export default App;