import React from 'react';
import LineChart from './LineChart';

const ChartCard = ({ coin, priceType, data }) => {
  const getPercentageChange = () => {
    if (!data || data.length < 2) return 0;
    const latest = data[data.length - 1][priceType];
    const previous = data[data.length - 2][priceType];
    return ((latest - previous) / previous) * 100;
  };

  const getLatestPrice = () => {
    if (!data || !data.length) return 0;
    return data[data.length - 1][priceType];
  };

  return (
    <div style={{
      background: 'white',
      borderRadius: '15px',
      padding: '20px',
      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
      display: 'flex',
      flexDirection: 'column',
      flex: 1,
      minWidth: '3000px' // Increase minWidth to accommodate longer chart
    }}>
      <div style={{ marginBottom: '15px' }}>
        <h2 style={{ 
          margin: '0 0 10px 0',
          fontSize: '24px',
          fontWeight: 'bold'
        }}>
          {`${coin} ${priceType.toUpperCase()}`}
        </h2>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <PriceChange value={getPercentageChange()} />
          <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
            ${getLatestPrice().toLocaleString()}
          </div>
        </div>
      </div>
      <LineChart 
        data={data}
        priceType={priceType}
        coin={coin}
      />
    </div>
  );
};

// Helper component for price change display
const PriceChange = ({ value }) => {
  const isPositive = value > 0;
  return (
    <div style={{
      color: isPositive ? '#2ecc71' : '#e74c3c',
      fontSize: '16px',
      fontWeight: '500',
      display: 'flex',
      alignItems: 'center',
      gap: '4px'
    }}>
      {isPositive ? '↑' : '↓'} {Math.abs(value).toFixed(2)}%
    </div>
  );
};

export default ChartCard;
