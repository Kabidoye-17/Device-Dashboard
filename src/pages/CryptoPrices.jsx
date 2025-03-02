import React, { useState, useEffect } from 'react';
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
          BTC: [...prev.BTC.slice(-19), metricsData.BTC],
          ETH: [...prev.ETH.slice(-19), metricsData.ETH]
        }));
        
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
          justifyContent: 'space-between', 
          gap: '20px'
        }}>
          <ChartCard 
            key={`BTC-price-${historicalData.BTC[historicalData.BTC.length - 1]?.timestamp}`}
            coin="BTC"
            priceType="price"
            data={historicalData.BTC}
          />
          <ChartCard 
            key={`BTC-ask-${historicalData.BTC[historicalData.BTC.length - 1]?.timestamp}`}
            coin="BTC"
            priceType="ask"
            data={historicalData.BTC}
          />
          <ChartCard 
            key={`BTC-bid-${historicalData.BTC[historicalData.BTC.length - 1]?.timestamp}`}
            coin="BTC"
            priceType="bid"
            data={historicalData.BTC}
          />
        </div>

        {/* ETH Charts */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          gap: '20px'
        }}>
          <ChartCard 
            key={`ETH-price-${historicalData.ETH[historicalData.ETH.length - 1]?.timestamp}`}
            coin="ETH"
            priceType="price"
            data={historicalData.ETH}
          />
          <ChartCard 
            key={`ETH-ask-${historicalData.ETH[historicalData.ETH.length - 1]?.timestamp}`}
            coin="ETH"
            priceType="ask"
            data={historicalData.ETH}
          />
          <ChartCard 
            key={`ETH-bid-${historicalData.ETH[historicalData.ETH.length - 1]?.timestamp}`}
            coin="ETH"
            priceType="bid"
            data={historicalData.ETH}
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
