import React, { useState, useEffect } from 'react';
import { apiUrl } from '../config';
import { ErrorContainer, RetryButton, MetricsGrid } from '../styles/StyledComponents';

function SystemMetrics() {
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
        const response = await fetch(`${apiUrl}/metrics/latest-batch`);
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        
        // Transform metrics data
        const metricsData = {
          cpu_load: 0,
          ram_usage: 0,
          network_sent: 0,
          timestamp: new Date().toISOString()
        };

        data.forEach(metric => {
          if (metric.name === 'CPU_LOAD') metricsData.cpu_load = metric.value;
          if (metric.name === 'RAM_USAGE') metricsData.ram_usage = metric.value;
          if (metric.name === 'NETWORK_SENT') metricsData.network_sent = metric.value;
          metricsData.timestamp = metric.timestamp;
        });

        setMetrics(metricsData);
        setError(null);
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
      <MetricsGrid>
        <div>CPU Load: {metrics.cpu_load}%</div>
        <div>RAM Usage: {metrics.ram_usage}%</div>
        <div>Network Sent: {metrics.network_sent} MB</div>
        <div>Last Updated: {new Date(metrics.timestamp).toLocaleString()}</div>
      </MetricsGrid>
    </div>
  );
}

export default SystemMetrics;
