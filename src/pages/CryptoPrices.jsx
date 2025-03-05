import React, { useState, useEffect, useMemo } from 'react';
import { apiUrl } from '../config';
import { ErrorContainer, RetryButton } from '../styles/StyledComponents';
import { Line } from 'react-chartjs-2';

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

  const renderChart = (data, coin) => {
    const chartData = {
      labels: data.map(entry => formatTimestamp(entry.timestamp)),
      datasets: [
        {
          label: 'Price',
          data: data.map(entry => entry.price),
          borderColor: 'blue',
          fill: false
        },
        {
          label: 'Ask',
          data: data.map(entry => entry.ask),
          borderColor: 'red',
          fill: false
        },
        {
          label: 'Bid',
          data: data.map(entry => entry.bid),
          borderColor: 'green',
          fill: false
        }
      ]
    };

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top', labels: { font: { size: 14 } } },
        tooltip: {
          mode: 'index',
          intersect: false,
          callbacks: {
            label: (context) => `${coin} ${context.dataset.label}: $${context.raw.toFixed(2)}`
          }
        }
      },
      scales: {
        x: {
          display: false // Hide x-axis labels
        },
        y: {
          grid: { color: 'rgba(0, 0, 0, 0.1)' },
          ticks: {
            callback: (value) => `$${value.toFixed(2)}`
          }
        }
      },
      elements: { line: { tension: 0.3 }, point: { radius: 0, hoverRadius: 5 } },
      animation: { duration: 0 }
    };

    return (
      <div>
        <h2>{coin} Chart</h2>
        <Line data={chartData} options={options} />
      </div>
    );
  };

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
        {/* BTC Chart */}
        {renderChart(memoizedHistoricalData.BTC, 'BTC')}

        {/* ETH Chart */}
        {renderChart(memoizedHistoricalData.ETH, 'ETH')}

      </div>
    </div>
  );
}

export default CryptoPrices;
