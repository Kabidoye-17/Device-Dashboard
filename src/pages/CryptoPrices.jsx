import React, { useState, useEffect } from 'react';
import { apiUrl } from '../config';
import { ErrorContainer, RetryButton, GridContainer, Card } from '../styles/StyledComponents';
import { data } from 'react-router-dom';

function CryptoPrices() {
  const [cryptoPrices, setCryptoPrices] = useState({});
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCryptoPrices = async () => {
      try {
        const response = await fetch(`${apiUrl}/api/metrics/latest-batch`);
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        
        console.log('Raw API response:', data); // Debug log

    
        const cryptoData = {};

        data.forEach(metric => {
          if (metric.type === 'crypto') {
            const { name, value, timestamp } = metric;
            const [symbol, metricType] = name.split(' ');
            
            if (!cryptoData[symbol]) {
              cryptoData[symbol] = { price: null, bid: null, ask: null, timestamp: null };
            }

            if (metricType === 'Price') {
              cryptoData[symbol].price = value;
            } else if (metricType === 'Bid') {
              cryptoData[symbol].bid = value;
            } else if (metricType === 'Ask') {
              cryptoData[symbol].ask = value;
            }
            cryptoData[symbol].timestamp = timestamp;
          }
        });

        console.log('Processed crypto data:', cryptoData); // Debug log
        setCryptoPrices(cryptoData);
        setError(null);
      } catch (error) {
        console.error('Fetch error:', error);
        setError(error.message);
      }
    };

    fetchCryptoPrices();
    const interval = setInterval(fetchCryptoPrices, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const formatPrice = (price, decimals = 2) => {
    if (price === null) return 'Loading...';
    return `$${Number(price).toFixed(decimals)}`;
  };

  const renderCryptoCard = (symbol, data, decimals = 2) => (
    <Card key={symbol}>
      <h3>{symbol}</h3>
      <p>Price: {formatPrice(data?.price, decimals)}</p>
      <p>Bid: {formatPrice(data?.bid, decimals)}</p>
      <p>Ask: {formatPrice(data?.ask, decimals)}</p>
      <p>Last Updated: {data?.timestamp ? new Date(data.timestamp).toLocaleString() : 'Never'}</p>
    </Card>
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
      <h1>Cryptocurrency Prices</h1>

      <div>{data[0].name}</div>
    </div>
  );
}

export default CryptoPrices;
