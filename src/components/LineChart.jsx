import React, { useEffect, useState, useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Line } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const LineChart = ({ data, priceType, coin }) => {
  const getChartColors = useMemo(() => (type) => {
    switch(type) {
      case 'ask':
        return {
          bg: 'rgba(46, 204, 113, 0.2)',
          border: 'rgba(46, 204, 113, 1)'
        };
      case 'bid':
        return {
          bg: 'rgba(231, 76, 60, 0.2)',
          border: 'rgba(231, 76, 60, 1)'
        };
      default:
        return {
          bg: 'rgba(247, 147, 26, 0.2)',
          border: 'rgba(247, 147, 26, 1)'
        };
    }
  }, []); // Memoize the color function

  const colors = useMemo(() => getChartColors(priceType), [getChartColors, priceType]);

  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [{
      label: `${coin}/${priceType.toUpperCase()}`,
      data: [],
      fill: true,
      backgroundColor: colors.bg,
      borderColor: colors.border,
      tension: 0.3,
      pointRadius: 0,
      pointHoverRadius: 5,
    }]
  });

  useEffect(() => {
    if (data && data.length > 0) {
      setChartData({
        labels: data.map(entry => new Date(entry.timestamp).toLocaleTimeString()),
        datasets: [{
          label: `${coin}/${priceType.toUpperCase()}`,
          data: data.map(entry => entry[priceType]),
          fill: true,
          backgroundColor: colors.bg,
          borderColor: colors.border,
          tension: 0.3,
          pointRadius: 0,
          pointHoverRadius: 5,
        }]
      });
    }
  }, [data, priceType, coin, colors.bg, colors.border]); // Include all dependencies

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          font: {
            size: 14,
            family: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
          }
        }
      },
      title: {
        display: false // Remove title from chart
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleFont: {
          size: 14
        },
        bodyFont: {
          size: 14
        },
        padding: 12,
        callbacks: {
          title: (tooltipItems) => {
            return `Time: ${tooltipItems[0].label}`;
          },
          label: (context) => {
            const value = Number(context.raw).toLocaleString('en-US', {
              style: 'currency',
              currency: 'USD',
              minimumFractionDigits: 2
            });
            return `${coin} ${priceType.toUpperCase()}: ${value}`;
          }
        }
      }
    },
    scales: {
      x: {
        type: 'category',
        grid: {
          display: false
        },
        ticks: {
          maxTicksLimit: 10, // Limit the number of x-axis labels
          maxRotation: 45,
          autoSkip: true
        },
        reverse: false // Ensure newest data shows on the right
      },
      y: {
        type: 'linear',
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.1)'
        },
        ticks: {
          callback: (value) => `$${value.toLocaleString()}`,
          stepSize: 0.1, // smaller step size for more detailed scale
          maxTicksLimit: 20 // more ticks on the y-axis
        }
      }
    },
    elements: {
      line: {
        tension: 0.3 // slight curve to make the line smoother
      },
      point: {
        radius: 2 // smaller points for cleaner look
      }
    },
    animation: {
      duration: 0 // disable animation for immediate updates
    }
  };

  return (
    <div style={{ 
      background: 'white', 
      borderRadius: '15px',
      padding: '15px',
      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
      height: '350px',
      flex: '1',
      minWidth: '300px'
    }}>
      <Line data={chartData} options={options} key={coin} />
    </div>
  );
};

export default React.memo(LineChart); // Prevent unnecessary re-renders
