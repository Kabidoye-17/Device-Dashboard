import React, { useState, useEffect, useMemo } from 'react';
import { apiUrl } from '../config';
import ChartCard from '../components/ChartCard';
import { ErrorContainer, RetryButton, MetricsGrid } from '../styles/StyledComponents';

function CryptoPrices() {
  const [cryptoMetrics, setCryptoMetrics] = useState({
    BTC: { price: 0, bid: 0, ask: 0, timestamp: '-' },
    ETH: { price: 0, bid: 0, ask: 0, timestamp: '-' }
  });
  const [historicalData, setHistoricalData] = useState({
    BTC: [],
    ETH: []
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

        const metricsData = {
          BTC: { price: 0, bid: 0, ask: 0, timestamp: '-' },
          ETH: { price: 0, bid: 0, ask: 0, timestamp: '-' }
        };

        data.forEach(metric => {
          if (!metric || typeof metric !== 'object' || metric.type !== 'crypto') return;
          const value = parseFloat(metric.value) || 0;

          ['BTC', 'ETH'].forEach(coin => {
            if (metric.name.startsWith(`${coin}-USD`)) {
              if (metric.name.includes('Price')) metricsData[coin].price = value;
              else if (metric.name.includes('Bid')) metricsData[coin].bid = value;
              else if (metric.name.includes('Ask')) metricsData[coin].ask = value;
              metricsData[coin].timestamp = metric.timestamp;
            }
          });
        });

        // Update historical data
        setHistoricalData(prev => ({
          BTC: [...prev.BTC.slice(1), metricsData.BTC], // Slide back the times
          ETH: [...prev.ETH.slice(1), metricsData.ETH]  // Slide back the times
        }));
        
        setCryptoMetrics(metricsData);
      } catch (error) {
        console.error('Fetch error:', error);
        setError(error.message);
      }
    };

    fetchCryptoMetrics();
    const interval = setInterval(fetchCryptoMetrics, 10000);
    return () => clearInterval(interval);
  }, []);

  // Memoize the historical data for each chart
  const memoizedHistoricalData = useMemo(() => ({
    BTC: historicalData.BTC,
    ETH: historicalData.ETH
  }), [historicalData.BTC, historicalData.ETH]);

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
      
      {/* Charts Section */}
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column',
        gap: '20px',
        marginBottom: '30px'
      }}>
        {/* BTC Charts */}
        <div style={{ 
          display: 'flex', 
          flexWrap: 'wrap', // Allow wrapping
          justifyContent: 'space-between', 
          gap: '20px'
        }}>
          <ChartCard 
            coin="BTC"
            priceType="price"
            data={memoizedHistoricalData.BTC}
          />
          <ChartCard 
            coin="BTC"
            priceType="ask"
            data={memoizedHistoricalData.BTC}
          />
          <ChartCard 
            coin="BTC"
            priceType="bid"
            data={memoizedHistoricalData.BTC}
          />
        </div>

        {/* ETH Charts */}
        <div style={{ 
          display: 'flex', 
          flexWrap: 'wrap', // Allow wrapping
          justifyContent: 'space-between', 
          gap: '20px'
        }}>
          <ChartCard 
            coin="ETH"
            priceType="price"
            data={memoizedHistoricalData.ETH}
          />
          <ChartCard 
            coin="ETH"
            priceType="ask"
            data={memoizedHistoricalData.ETH}
          />
          <ChartCard 
            coin="ETH"
            priceType="bid"
            data={memoizedHistoricalData.ETH}
          />
        </div>
      </div>

      {/* Existing Metrics Grid */}
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
