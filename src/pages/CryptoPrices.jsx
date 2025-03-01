import React, { useState, useEffect } from 'react';
import { apiUrl } from '../config';
import { ErrorContainer, RetryButton, MetricsGrid } from '../styles/StyledComponents';

function CryptoPrices() {
  const [cryptoMetrics, setCryptoMetrics] = useState({
    BTC: { price: 0, bid: 0, ask: 0, timestamp: '-' },
    ETH: { price: 0, bid: 0, ask: 0, timestamp: '-' }
  });
  const [error, setError] = useState(null);

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    try {
      const date = new Date(timestamp);
      if (isNaN(date.getTime())) {
        console.warn('Invalid timestamp:', timestamp);
        return 'Invalid timestamp';
      }
      return date.toLocaleString('en-US', { dateStyle: 'medium', timeStyle: 'medium' });
    } catch (error) {
      console.error('Error formatting timestamp:', error);
      return 'Error formatting time';
    }
  };

  useEffect(() => {
    const fetchCryptoMetrics = async () => {
      try {
        const response = await fetch(`${apiUrl}/api/metrics/latest-batch`);
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        
        console.log('Raw crypto data:', data);

        const metricsData = {
          BTC: { price: 0, bid: 0, ask: 0, timestamp: '-' },
          ETH: { price: 0, bid: 0, ask: 0, timestamp: '-' }
        };

        data.forEach(metric => {
          if (!metric || typeof metric !== 'object' || metric.type !== 'crypto') return;
          const value = parseFloat(metric.value) || 0;

          if (metric.name.startsWith('BTC-USD')) {
            if (metric.name.includes('Price')) metricsData.BTC.price = value;
            else if (metric.name.includes('Bid')) metricsData.BTC.bid = value;
            else if (metric.name.includes('Ask')) metricsData.BTC.ask = value;
            metricsData.BTC.timestamp = metric.timestamp;
          }
          
          if (metric.name.startsWith('ETH-USD')) {
            if (metric.name.includes('Price')) metricsData.ETH.price = value;
            else if (metric.name.includes('Bid')) metricsData.ETH.bid = value;
            else if (metric.name.includes('Ask')) metricsData.ETH.ask = value;
            metricsData.ETH.timestamp = metric.timestamp;
          }
        });

        console.log('Processed crypto metrics:', metricsData);
        setCryptoMetrics(metricsData);
      } catch (error) {
        console.error('Fetch error:', error);
        setError(error.message);
      }
    };

    fetchCryptoMetrics();
    const interval = setInterval(fetchCryptoMetrics, 5000);
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
      <h1>Crypto Metrics</h1>
      <MetricsGrid>
        <div><strong>BTC-USD</strong></div>
        <div>Price: ${cryptoMetrics.BTC.price.toFixed(2)}</div>
        <div>Bid: ${cryptoMetrics.BTC.bid.toFixed(2)}</div>
        <div>Ask: ${cryptoMetrics.BTC.ask.toFixed(2)}</div>
        <div>Last Updated: {formatTimestamp(cryptoMetrics.BTC.timestamp)}</div>

        <div><strong>ETH-USD</strong></div>
        <div>Price: ${cryptoMetrics.ETH.price.toFixed(2)}</div>
        <div>Bid: ${cryptoMetrics.ETH.bid.toFixed(2)}</div>
        <div>Ask: ${cryptoMetrics.ETH.ask.toFixed(2)}</div>
        <div>Last Updated: {formatTimestamp(cryptoMetrics.ETH.timestamp)}</div>
      </MetricsGrid>
    </div>
  );
}

export default CryptoPrices;
