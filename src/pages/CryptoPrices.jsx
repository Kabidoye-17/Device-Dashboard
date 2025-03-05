import React, { useState, useEffect, useMemo } from 'react';
import { apiUrl } from '../config';
import ChartCard from '../components/ChartCard';
import { ErrorContainer, RetryButton } from '../styles/StyledComponents';

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
        const response = await fetch(`${apiUrl}/api/metrics/get-latest-metrics`);
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
              metricsData[coin].timestamp = metric.timestamp_utc;
            }
          });
        });

        // Initialize historical data with the latest 10 timestamps
        setHistoricalData(prev => {
          const newBTCData = [...prev.BTC, metricsData.BTC].slice(-10);
          const newETHData = [...prev.ETH, metricsData.ETH].slice(-10);
          return {
            BTC: newBTCData,
            ETH: newETHData
          };
        });
        
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

  const renderHistoricalTable = (data, coin) => (
    <table>
      <thead>
        <tr>
          <th>Timestamp</th>
          <th>Price</th>
          <th>Bid</th>
          <th>Ask</th>
        </tr>
      </thead>
      <tbody>
        {data.map((entry, index) => (
          <tr key={`${coin}-${index}`}>
            <td>{formatTimestamp(entry.timestamp)}</td>
            <td>{entry.price}</td>
            <td>{entry.bid}</td>
            <td>{entry.ask}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );

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
      <div>Last Updated: {formatTimestamp(cryptoMetrics.BTC.timestamp)}</div>
      
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

        {/* BTC Historical Data Table */}
        <div>
          <h2>BTC Historical Data</h2>
          {renderHistoricalTable(memoizedHistoricalData.BTC, 'BTC')}
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

        {/* ETH Historical Data Table */}
        <div>
          <h2>ETH Historical Data</h2>
          {renderHistoricalTable(memoizedHistoricalData.ETH, 'ETH')}
        </div>
      </div>
    </div>
  );
}

export default CryptoPrices;
