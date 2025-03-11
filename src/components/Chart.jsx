import React, { useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import 'chartjs-adapter-date-fns';
import { Button, MetricHeading } from '../styles/StyledComponents';
import { tradingSites, apiUrl } from '../config';
import Loading from './Loading';
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
);

const generateOptions = (min, max) => ({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      min,
      max,
    },
    x: {
      type: 'time',
      time: {
        unit: 'minute',
      },
      ticks: {
        source: 'data',
      },
    },
  },
  plugins: {
    legend: {
      position: 'top',
    },
    title: {
      display: true,
      text: 'Crypto Metrics',
    },
  },
});

const generateDatasets = (cryptoData, type) => {
  const datasets = [];
  const labels = cryptoData.map(item => new Date(item.timestamp_utc));

  const priceData = cryptoData.filter(item => item.name.includes('Price')).map(item => ({ x: new Date(item.timestamp_utc), y: item.value }));
  const askData = cryptoData.filter(item => item.name.includes('Ask')).map(item => ({ x: new Date(item.timestamp_utc), y: item.value }));
  const bidData = cryptoData.filter(item => item.name.includes('Bid')).map(item => ({ x: new Date(item.timestamp_utc), y: item.value }));

  datasets.push({
    label: `${type} Price`,
    data: priceData,
    borderColor: 'rgb(255, 99, 132)',
    backgroundColor: 'rgba(255, 99, 132, 0.5)',
  });

  datasets.push({
    label: `${type} Ask`,
    data: askData,
    borderColor: 'rgb(53, 162, 235)',
    backgroundColor: 'rgba(53, 162, 235, 0.5)',
  });

  datasets.push({
    label: `${type} Bid`,
    data: bidData,
    borderColor: 'rgb(75, 192, 192)',
    backgroundColor: 'rgba(75, 192, 192, 0.5)',
  });

  const allValues = [...priceData.map(d => d.y), ...askData.map(d => d.y), ...bidData.map(d => d.y)];
  const min = Math.min(...allValues);
  const max = Math.max(...allValues);

  return { labels, datasets, min, max };
};

const Chart = ({ cryptoData }) => {
  const [loading, setLoading] = useState(false);
  const cryptoTypes = [...new Set(cryptoData.map(item => item.name.split('-')[0]))];

  const openTradingSite = async (type) => {
    const site = type === 'BTC' ? tradingSites.BTC : tradingSites.ETH;
    setLoading(true);
    try {
      const response = await fetch(`${apiUrl}/api/recieve-site`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ site_url: site })
      });
      const data = await response.json();
      if (data.status === 'error') {
        console.error('Error opening site:', data.message);
      }
    } catch (error) {
      console.error('Error making request:', error);
    } finally {
      await new Promise(resolve => setTimeout(resolve, 5000));
      setLoading(false);
    }
  };

  return (
    <div style={{ overflowX: 'hidden' }}>
      {loading && <Loading />}
      {cryptoTypes.map(type => {
        const typeData = cryptoData.filter(item => item.name.split('-')[0] === type);
        const { datasets, min, max } = generateDatasets(typeData, type);
        const options = generateOptions(min, max);

        return (
          <div key={type} style={{ width: '100%', maxWidth: '100%' }}>
            <MetricHeading>{type} Metrics</MetricHeading>
            <Button onClick={() => openTradingSite(type)}>Open {type} trading site</Button>
            <div style={{ width: '100%', height: '800px' }}>
              <Line options={options} data={{ datasets }} />
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default Chart;
