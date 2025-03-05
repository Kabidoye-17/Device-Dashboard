import React, { useState, useEffect } from 'react';
import { apiUrl } from '../config';
import { ErrorContainer, RetryButton } from '../styles/StyledComponents';

function SystemMetrics() {
  const [metrics, setMetrics] = useState([]);
  const [error, setError] = useState(null);

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    try {
      const date = typeof timestamp === 'number' 
        ? new Date(timestamp * 1000)  // Unix timestamp
        : new Date(timestamp);        // ISO string
      
      if (isNaN(date.getTime())) {
        console.warn('Invalid timestamp:', timestamp);
        return 'Invalid timestamp';
      }
      
      return date.toLocaleString('en-US', {
        dateStyle: 'medium',
        timeStyle: 'medium'
      });
    } catch (error) {
      console.error('Error formatting timestamp:', error);
      return 'Error formatting time';
    }
  };

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch(`${apiUrl}/api/metrics/get-latest-metrics`);
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        
        console.log('Raw metrics data:', data);

        const formattedData = data.map(metric => ({
          name: metric.name,
          value: parseFloat(metric.value) || 0,
          timestamp: metric.timestamp_utc
        }));

        console.log('Formatted metrics:', formattedData);
        
        setMetrics(formattedData);
      } catch (error) {
        console.error('Fetch error:', error);
        setError(error.message);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  if (error) {
    return (
      <ErrorContainer>
        <p>Error: {error}</p>
        <RetryButton onClick={() => window.location.reload()}>
          Retry Connection
        </RetryButton>
      </ErrorContainer>
    );
  }

  return (
    <div>
      <h1>System Metrics</h1>
      {/* Display Metrics in Table */}
      <table>
        <thead>
          <tr>
            <th>Metric Name</th>
            <th>Value</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {metrics.map((metric, index) => (
            <tr key={index}>
              <td>{metric.name}</td>
              <td>{metric.value.toFixed(2)}</td>
              <td>{formatTimestamp(metric.timestamp)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default SystemMetrics;
