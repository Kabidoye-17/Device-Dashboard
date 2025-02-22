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
        
        const cryptoData = {
          BTC: { timestamp: null },
          ETH: { timestamp: null }
        };

        // Map backend metric names to frontend properties
        const metricMapping = {
          'BTC_PRICE': ['BTC', 'price'],
          'BTC_BID': ['BTC', 'bid'],
          'BTC_ASK': ['BTC', 'ask'],
          'ETH_PRICE': ['ETH', 'price'],
          'ETH_BID': ['ETH', 'bid'],
          'ETH_ASK': ['ETH', 'ask']
        };

        data.forEach(metric => {
          if (metric.name in metricMapping) {
            const [coin, field] = metricMapping[metric.name];
            if (!cryptoData[coin]) {
              cryptoData[coin] = { timestamp: metric.timestamp };
            }
            cryptoData[coin][field] = metric.value;
            cryptoData[coin].timestamp = metric.timestamp;
          }
        });

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
    return price ? `$${parseFloat(price).toFixed(decimals)}` : 'Loading...';
  };

  const renderCryptoCard = (symbol, data, decimals = 2) => (
    <Card>
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
