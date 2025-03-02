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
      case 'ask': return { bg: 'rgba(46, 204, 113, 0.2)', border: 'rgba(46, 204, 113, 1)' };
      case 'bid': return { bg: 'rgba(231, 76, 60, 0.2)', border: 'rgba(231, 76, 60, 1)' };
      default: return { bg: 'rgba(247, 147, 26, 0.2)', border: 'rgba(247, 147, 26, 1)' };
    }
  }, []);

  const colors = useMemo(() => getChartColors(priceType), [getChartColors, priceType]);

  const lastDataPoint = useMemo(() => data?.length ? data[data.length - 1] : null, [data]);

  const yAxisLimits = useMemo(() => {
    if (!lastDataPoint) return {};
    const currentValue = lastDataPoint[priceType];
    const range = currentValue * 0.0002; // 🔹 Tighter range (0.02% of price)
    return { min: currentValue - range, max: currentValue + range };
  }, [lastDataPoint, priceType]);

  const options = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'top', labels: { font: { size: 14 } } },
      tooltip: {
        mode: 'index',
        intersect: false,
        callbacks: {
          label: (context) => `${coin} ${priceType.toUpperCase()}: $${context.raw.toFixed(2)}` // 🔹 Show 2 decimal places
        }
      }
    },
    scales: {
      x: { type: 'category', grid: { display: false }, ticks: { maxTicksLimit: 10, maxRotation: 45 } },
      y: {
        type: 'linear',
        min: yAxisLimits.min,
        max: yAxisLimits.max,
        grid: { color: 'rgba(0, 0, 0, 0.1)' },
        ticks: {
          stepSize: (yAxisLimits.max - yAxisLimits.min) / 6, // 🔹 Smaller steps for visibility
          callback: (value) => `$${value.toFixed(2)}` // 🔹 Show 2 decimal places
        }
      }
    },
    elements: { line: { tension: 0.3 }, point: { radius: 0, hoverRadius: 5 } },
    animation: { duration: 0 }
  }), [coin, priceType, yAxisLimits]);

  const [chartData, setChartData] = useState({ labels: [], datasets: [] });

  useEffect(() => {
    if (!lastDataPoint) return;

    setChartData((prev) => {
      const newLabels = data.map(entry => new Date(entry.timestamp).toLocaleTimeString());
      const newData = data.map(entry => entry[priceType]);

      if (JSON.stringify(prev.labels) === JSON.stringify(newLabels) &&
          JSON.stringify(prev.datasets[0]?.data) === JSON.stringify(newData)) return prev;

      return {
        labels: newLabels,
        datasets: [{
          label: `${coin}/${priceType.toUpperCase()}`,
          data: newData,
          fill: true,
          backgroundColor: colors.bg,
          borderColor: colors.border,
          tension: 0.3,
          pointRadius: 0,
          pointHoverRadius: 5,
        }]
      };
    });
  }, [lastDataPoint, priceType, coin, colors, data]);

  return (
    <div style={{ 
      background: 'white', 
      borderRadius: '15px',
      padding: '15px',
      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
      height: '800px', // Increase height for better readability
      flex: '1',
      minWidth: '300px'
    }}>
      <Line data={chartData} options={options} key={coin} />
    </div>
  );
};

export default React.memo(LineChart);
