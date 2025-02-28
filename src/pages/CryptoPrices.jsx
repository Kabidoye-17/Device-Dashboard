import React, { useState, useEffect } from 'react';
import { apiUrl } from '../config';
import { ErrorContainer, RetryButton, GridContainer, Card } from '../styles/StyledComponents';

function CryptoPrices() {
  const [cryptoPrices, setCryptoPrices] = useState({
    BTC: null,
    ETH: null
  });
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCryptoPrices = async () => {
      try {
        const response = await fetch(`${apiUrl}/api/metrics/latest-batch`);
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        
        console.log('Raw API response:', data); // Debug log

        const cryptoData = {
          BTC: { price: 0, bid: 0, ask: 0, timestamp: null },
          ETH: { price: 0, bid: 0, ask: 0, timestamp: null }
        };

        data.forEach(metric => {
          if (!metric || typeof metric !== 'object') return;
          
          const value = parseFloat(metric.value) || 0;
          const name = metric.name;

          // Updated name matching for actual metric names
          if (name.startsWith('BTC-USD')) {
            if (name === 'BTC-USD Ask') {
              cryptoData.BTC.ask = value;
              cryptoData.BTC.timestamp = metric.timestamp;
            } else if (name === 'BTC-USD Bid') {
              cryptoData.BTC.bid = value;
              cryptoData.BTC.timestamp = metric.timestamp;
            } else if (name === 'BTC-USD Price') {
              cryptoData.BTC.price = value;
              cryptoData.BTC.timestamp = metric.timestamp;
            }
          } else if (name.startsWith('ETH-USD')) {
            if (name === 'ETH-USD Ask') {
              cryptoData.ETH.ask = value;
              cryptoData.ETH.timestamp = metric.timestamp;
            } else if (name === 'ETH-USD Bid') {
              cryptoData.ETH.bid = value;
              cryptoData.ETH.timestamp = metric.timestamp;
            } else if (name === 'ETH-USD Price') {
              cryptoData.ETH.price = value;
              cryptoData.ETH.timestamp = metric.timestamp;
            }
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
    if (!price && price !== 0) return 'Loading...';
    return `$${Number(price).toFixed(decimals)}`;
  };

  const renderCryptoCard = (symbol, data, decimals = 2) => (
    <Card>
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
      <GridContainer>
        {renderCryptoCard('Bitcoin (BTC)', cryptoPrices.BTC, 2)}
        {renderCryptoCard('Ethereum (ETH)', cryptoPrices.ETH, 2)}
      </GridContainer>
    </div>
  );
}

export default CryptoPrices;
