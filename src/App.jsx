import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { Container} from './styles/StyledComponents';
import { apiUrl } from '../config';
import styled from 'styled-components';

export const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
  
  th, td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #ddd;
  }

  th {
    background-color: #f2f2f2;
    font-weight: bold;
  }

  tr:hover {
    background-color: #f5f5f5;
  }
`;

function App() {
  const [historicalCryptoData, setHistoricalCryptoData] = useState([]);
  const [cryptoMetrics, setCryptoMetrics] = useState();

  const [historicalSystemData, setHistoricalSystemData] = useState([]);
  const [systemMetrics, setSystemMetrics] = useState();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${apiUrl}/api/metrics/get-latest-metrics`);
        const data = await response.json();
        
        const formattedData = data.map(item => ({
          deviceName: item.device_name,
          name: item.name,
          value: item.value,
          unit: item.unit,
          timestamp_utc: item.timestamp_utc,
          utc_offset: item.utc_offset
        }));

        const systemData = formattedData.filter(item => item.type === 'system');
        const cryptoData = formattedData.filter(item => item.type === 'crypto');

        setHistoricalSystemData(systemData);
        setSystemMetrics(systemData[0]);
        setHistoricalCryptoData(cryptoData);
        setCryptoMetrics(cryptoData[0]);
        
      } catch (error) {
        console.error('Error fetching metrics:', error);
      }
    };
    fetchData();
    const intervalId = setInterval(fetchData, 5000); // Fetch every minute

    return () => clearInterval(intervalId);
  }, []);

  return (
    <Router basename="/Device-Dashboard">
      <Container>
        {/* Latest System Metrics */}
        <div>
          <h2>Latest System Metrics</h2>
          {systemMetrics && (
            <div>
              <p>Device: {systemMetrics.deviceName}</p>
              <p>{systemMetrics.name}: {systemMetrics.value} {systemMetrics.unit}</p>
              <p>Time: {new Date(systemMetrics.timestamp_utc).toLocaleString()}</p>
            </div>
          )}
  
          {/* System Metrics History Table */}
          <h3>System Metrics History</h3>
          <table>
            <thead>
              <tr>
                <th>Device</th>
                <th>Metric</th>
                <th>Value</th>
                <th>Unit</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {historicalSystemData.map((metric, index) => (
                <tr key={index}>
                  <td>{metric.deviceName}</td>
                  <td>{metric.name}</td>
                  <td>{metric.value}</td>
                  <td>{metric.unit}</td>
                  <td>{new Date(metric.timestamp_utc).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
  
        {/* Latest Crypto Metrics */}
        <div>
          <h2>Latest Crypto Metrics</h2>
          {cryptoMetrics && (
            <div>
              <p>Currency: {cryptoMetrics.deviceName}</p>
              <p>{cryptoMetrics.name}: {cryptoMetrics.value} {cryptoMetrics.unit}</p>
              <p>Time: {new Date(cryptoMetrics.timestamp_utc).toLocaleString()}</p>
            </div>
          )}
  
          {/* Crypto Metrics History Table */}
          <h3>Crypto Price History</h3>
          <table>
            <thead>
              <tr>
                <th>Currency</th>
                <th>Metric</th>
                <th>Value</th>
                <th>Unit</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {historicalCryptoData.map((metric, index) => (
                <tr key={index}>
                  <td>{metric.deviceName}</td>
                  <td>{metric.name}</td>
                  <td>{metric.value}</td>
                  <td>{metric.unit}</td>
                  <td>{new Date(metric.timestamp_utc).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Container>
    </Router>
  );
}

export default App;