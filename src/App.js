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
    ETH: null,
    DOGE: null
  });

  const [error, setError] = useState(null);

  // System metrics useEffect
  useEffect(() => {
    const fetchSystemMetrics = async () => {
      try {
        const response = await fetch(`${apiUrl}/system-metrics`);
        const data = await response.json();
        setMetrics(data);
      } catch (error) {
        console.error('System metrics error:', error);
        setError(error.message);
      }
    };
    fetchSystemMetrics();

    return () => {};
  }, []);

  // Crypto prices useEffect
  useEffect(() => {
    const fetchCryptoPrices = async () => {
      try {
        const pairs = ['BTC-USD', 'ETH-USD', 'DOGE-USD'];
        const responses = await Promise.all(
          pairs.map(pair => 
            fetch(`${apiUrl}/crypto-ticker/${pair}`)
              .then(res => res.json())
          )
        );

        setCryptoPrices({
          BTC: responses[0],
          ETH: responses[1], 
          DOGE: responses[2]
        });
        setError(null);
      } catch (error) {
        console.error('Crypto error:', error);
        setError(error.message);
      }
    };

    fetchCryptoPrices();
    return () => {};
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
          <p>Last Updated: {data.timestamp}</p>
        </>
      ) : (
        <p>Loading {symbol} data...</p>
      )}
    </div>
  );

  return (
    <div style={{ padding: '20px' }}>
      {error ? (
        <p style={{ color: 'red' }}>Error: {error}</p>
      ) : (
        <>
          <div style={{ marginBottom: '20px' }}>
            <h2>System Metrics</h2>
            <p>CPU Load: {metrics.cpu_load}%</p>
            <p>RAM Usage: {metrics.ram_usage}%</p>
            <p>Network Data Sent: {metrics.network_sent} MB</p>
            <p>Last Updated: {metrics.timestamp}</p>
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