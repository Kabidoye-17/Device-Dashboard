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
        console.log('Fetched Data:', data); // Log the fetched data

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

        // Initialize historical data with the latest fetched metrics and add to the history
        setHistoricalData(prev => {
          const newBTCData = [{ ...metricsData.BTC, timestamp: metricsData.BTC.timestamp }, ...prev.BTC].slice(0, 10);
          const newETHData = [{ ...metricsData.ETH, timestamp: metricsData.ETH.timestamp }, ...prev.ETH].slice(0, 10);
          console.log('Updated Historical Data BTC:', newBTCData); // Log historical data for BTC
          console.log('Updated Historical Data ETH:', newETHData); // Log historical data for ETH
          return {
            BTC: newBTCData,
            ETH: newETHData
          };
        });

        setCryptoMetrics(metricsData);
        console.log('Updated Crypto Metrics:', metricsData); // Log the updated crypto metrics

      } catch (error) {
        console.error('Fetch error:', error);
        setError(error.message);
      }
    };

    fetchCryptoMetrics();
    const interval = setInterval(fetchCryptoMetrics, 5000);
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

      {/* Display Current Values */}
      <div>
        <h1>BTC - Price: ${cryptoMetrics.BTC.price.toFixed(2)}</h1>
        <h1>Bid: ${cryptoMetrics.BTC.bid.toFixed(2)}</h1>
        <h1>Ask: ${cryptoMetrics.BTC.ask.toFixed(2)}</h1>
        <h1>Last Updated: {formatTimestamp(cryptoMetrics.BTC.timestamp)}</h1>
      </div>

      <div>
        <h1>ETH - Price: ${cryptoMetrics.ETH.price.toFixed(2)}</h1>
        <h1>Bid: ${cryptoMetrics.ETH.bid.toFixed(2)}</h1>
        <h1>Ask: ${cryptoMetrics.ETH.ask.toFixed(2)}</h1>
        <h1>Last Updated: {formatTimestamp(cryptoMetrics.ETH.timestamp)}</h1>
      </div>

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
