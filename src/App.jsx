import React, { useState, useEffect } from 'react';
import { apiUrl } from './config';

function App() {
  const [metrics, setMetrics] = useState({
    cpu_load: 0,
    ram_usage: 0, 
    network_sent: 0,
    timestamp: '-'
  });

  const [cryptoPrices, setCryptoPrices] = useState({
    BTC: null,
    ETH: null
  });

  const [error, setError] = useState(null);

  // Combined data fetching in single useEffect
  useEffect(() => {
    const fetchAllData = async () => {
      try {
        // Fetch metrics
        const metricsRes = await fetch(`${apiUrl}/system-metrics`);
        const metricsData = await metricsRes.json();
        if (metricsRes.ok) {
          setMetrics(metricsData);
        }

        // Fetch all crypto pairs at once
        const cryptoData = {};
        for (const pair of ['BTC-USD', 'ETH-USD']) {
          const res = await fetch(`${apiUrl}/crypto-ticker/${pair}`);
          if (res.ok) {
            const data = await res.json();
            cryptoData[pair.split('-')[0]] = data;
          }
        }
        
        if (Object.keys(cryptoData).length > 0) {
          setCryptoPrices(cryptoData);
          setError(null);
        }
      } catch (error) {
        console.error('Fetch error:', error);
        setError(error.message);
      }
    };

    fetchAllData();
  }, []);

  const formatPrice = (price, decimals = 2) => {
    return price ? `$${parseFloat(price).toFixed(decimals)}` : 'Loading...';
  };

  const renderCryptoCard = (symbol, data, decimals = 2) => (
    <div style={{ 
      background: '#f5f5f5', 
      padding: '20px',
      borderRadius: '8px',
      margin: '10px'
    }}>
      <h3>{symbol}</h3>
      {data ? (
        <>
          <p>Price: {formatPrice(data.price, decimals)}</p>
          <p>Bid: {formatPrice(data.bid, decimals)}</p>
          <p>Ask: {formatPrice(data.ask, decimals)}</p>
          <p>Last Updated: {new Date(data.timestamp).toLocaleString()}</p>
        </>
      ) : (
        <p>Loading {symbol} data...</p>
      )}
    </div>
  );

  return (
    <div style={{ padding: '20px' }}>
      {error ? (
        <div style={{ color: 'red', textAlign: 'center', padding: '20px' }}>
          <p>Error: {error}</p>
          <button onClick={() => window.location.reload()}>
            Retry Connection
          </button>
        </div>
      ) : (
        <>
          <h1>Device Dashboard</h1>
          <div style={{ marginBottom: '20px' }}>
            <h2>System Metrics</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
              <div>CPU Load: {metrics.cpu_load}%</div>
              <div>RAM Usage: {metrics.ram_usage}%</div>
              <div>Network Sent: {metrics.network_sent} MB</div>
              <div>Last Updated: {new Date(metrics.timestamp).toLocaleString()}</div>
            </div>
          </div>

          <div>
            <h2>Cryptocurrency Prices</h2>
            <div style={{ 
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
              gap: '20px'
            }}>
              {renderCryptoCard('Bitcoin (BTC)', cryptoPrices.BTC, 2)}
              {renderCryptoCard('Ethereum (ETH)', cryptoPrices.ETH, 2)}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default App;