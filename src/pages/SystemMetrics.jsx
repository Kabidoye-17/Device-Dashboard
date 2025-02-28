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

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    try {
      // Handle both Unix timestamps and ISO strings
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
        const response = await fetch(`${apiUrl}/api/metrics/latest-batch`);
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        
        console.log('Received metrics data:', data); // Debug log

        if (!Array.isArray(data)) {
          console.error('Expected array of metrics, got:', typeof data);
          return;
        }

        const metricsData = {
          cpu_load: 0,
          ram_usage: 0,
          network_sent: 0,
          timestamp: null
        };

        // Map backend metric names to frontend properties and handle numerical conversions
        data.forEach(metric => {
          if (!metric || typeof metric !== 'object') return;
          
          const value = parseFloat(metric.value) || 0;
          
          switch(metric.name) {
            case 'CPU_LOAD':
              metricsData.cpu_load = value;
              break;
            case 'RAM_USAGE':
              metricsData.ram_usage = value;
              break;
            case 'NETWORK_SENT':
              metricsData.network_sent = value;
              break;
            default:
              console.debug('Unhandled metric:', metric.name);
          }

          if (!metricsData.timestamp && metric.timestamp) {
            metricsData.timestamp = metric.timestamp;
          }
        });

        console.log('Processed metrics data:', metricsData); // Debug log
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
        <div>CPU Load: {Number.isFinite(metrics.cpu_load) ? metrics.cpu_load.toFixed(2) : '0.00'}%</div>
        <div>RAM Usage: {Number.isFinite(metrics.ram_usage) ? metrics.ram_usage.toFixed(2) : '0.00'}%</div>
        <div>Network Sent: {Number.isFinite(metrics.network_sent) ? metrics.network_sent.toFixed(2) : '0.00'} MB</div>
        <div>Last Updated: {formatTimestamp(metrics.timestamp)}</div>
      </MetricsGrid>
    </div>
  );
}

export default SystemMetrics;
