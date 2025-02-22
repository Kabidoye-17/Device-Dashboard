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
        const response = await fetch(`${apiUrl}/api/metrics/latest-batch`);
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        
        const metricsData = {
          cpu_load: 0,
          ram_usage: 0,
          network_sent: 0,
          timestamp: null
        };

        // Map backend metric names to frontend properties
        const metricMapping = {
          'CPU_LOAD': 'cpu_load',
          'RAM_USAGE': 'ram_usage',
          'NETWORK_SENT': 'network_sent'
        };

        data.forEach(metric => {
          if (metric.name in metricMapping) {
            metricsData[metricMapping[metric.name]] = metric.value;
            metricsData.timestamp = metric.timestamp;
          }
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
