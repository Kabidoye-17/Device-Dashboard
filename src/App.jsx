import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { HeaderBanner, MetricHeading, Button, GaugeContainer, ChoiceContainer} from './styles/StyledComponents';
import { apiUrl } from './config';
import styled from 'styled-components';
import getSymbolFromCurrency from 'currency-symbol-map'
import Gauge from './components/Gauge';
import Chart from './components/Chart';

export const StyledTable = styled.table`
  border-collapse: separate;
  border-spacing: 0;
  width: 100%;
  font-size: 0.9em;
  font-family: sans-serif;
`;
export const TableHeader = styled.thead`
  background-color: #009879;
  color: #ffffff;
  text-align: left;
  position: sticky;
  top: 0;
  z-index: 1;
`;

export const TableHeaderRow = styled.tr``;

export const TableCell = styled.td`
  padding: 12px 15px;
`;

export const TableHeaderCell = styled.th`
  padding: 12px 15px;
  background-color: #009879;
  border-bottom: 2px solid #006B56;
`;

export const TableBody = styled.tbody``;

export const TableRow = styled.tr`
  border-bottom: 1px solid #dddddd;
  
  &:nth-of-type(even) {
    background-color: #f3f3f3;
  }

  &:last-of-type {
    border-bottom: 2px solid #009879;
  }

  &.active-row {
    font-weight: bold;
    color: #009879;
  }
`;
export const TableContainer = styled.div`
  max-height: 600px;
  overflow-y: auto;
  overflow-x: hidden; /* Prevent horizontal scroll */
  margin-bottom: 20px;
  border-radius: 4px;
  width: 100%;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);

  /* Style for webkit browsers */
  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: #f1f1f1;
  }

  &::-webkit-scrollbar-thumb {
    background: #009879;
    border-radius: 4px;
  }

  /* Style for Firefox */
  scrollbar-width: thin;
  scrollbar-color: #009879 #f1f1f1;
`;

function App() {
  const [historicalCryptoData, setHistoricalCryptoData] = useState([]);
  const [cryptoMetrics, setCryptoMetrics] = useState([]);

  const [historicalSystemData, setHistoricalSystemData] = useState([]);
  const [systemMetrics, setSystemMetrics] = useState([]);

  const [showSystemTable, setShowSystemTable] = useState(false);
  const [showCryptoTable, setShowCryptoTable] = useState(false);

  const [selectedMetricValue, setSelectedMetricValue] = useState();
  const [selectedMetricName, setSelectedMetricName] = useState();

  const toggleSystemTable = () => setShowSystemTable(!showSystemTable);
  const toggleCryptoTable = () => setShowCryptoTable(!showCryptoTable)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${apiUrl}/api/metrics/get-latest-metrics`);
        const data = await response.json();
        
        if (data && data.length > 0) {
          const formattedData = data.map(item => ({
            deviceName: item.device_name,
            name: item.name,
            value: item.value,
            unit: item.unit,
            timestamp_utc: item.timestamp_utc,
            utc_offset: item.utc_offset,
            type: item.type // Ensure type is included
          }));

          const metricOrder = {
            'CPU Load': 1,
            'RAM Usage': 2,
            'Network Sent': 3
          };

          const cryptoOrder = {
            'ETH': 1,
            'BTC': 2
          };
  
          const cryptoMetricOrder = {
            'Price': 1,
            'Ask': 2,
            'Bid': 3
          };
  
          // Sort system data by timestamp and metric order
          const systemData = formattedData
            .filter(item => item.type === 'system')
            .sort((a, b) => {
              // First compare timestamps (newest first)
              const timeCompare = new Date(b.timestamp_utc) - new Date(a.timestamp_utc);
              if (timeCompare !== 0) return timeCompare;
              // If same timestamp, sort by metric order
              return metricOrder[a.name] - metricOrder[b.name];
            });

          // Set default selected metric value to the first percentage metric
          const firstPercentageMetric = systemData.find(metric => metric.unit === '%');
          if (!selectedMetricName && firstPercentageMetric) {
            setSelectedMetricValue(firstPercentageMetric.value);
            setSelectedMetricName(firstPercentageMetric.name);
          } else if (selectedMetricName) {
            const updatedMetric = systemData.find(metric => metric.name === selectedMetricName);
            if (updatedMetric) {
              setSelectedMetricValue(updatedMetric.value);
            }
          }

          // Sort crypto data
          const cryptoData = formattedData
          .filter(item => item.type === 'crypto')
          .sort((a, b) => {
            // First compare timestamps (newest first)
            const timeCompare = new Date(b.timestamp_utc) - new Date(a.timestamp_utc);
            if (timeCompare !== 0) return timeCompare;
            
            // Extract currency from name (ETH or BTC)
            const currencyA = a.name.split('-')[0];
            const currencyB = b.name.split('-')[0];
            
            // Compare currencies first (ETH vs BTC)
            if (currencyA !== currencyB) {
              return cryptoOrder[currencyA] - cryptoOrder[currencyB];
            }
            
            // Extract metric type (Price, Ask, Bid)
            const metricA = a.name.split(' ')[1];
            const metricB = b.name.split(' ')[1];
            
            // Compare metric types
            return cryptoMetricOrder[metricA] - cryptoMetricOrder[metricB];
          });
          setHistoricalSystemData(systemData);
          
          setSystemMetrics(systemData.length > 0 ? systemData.slice(0, 3) : []);
          setHistoricalCryptoData(cryptoData);
          setCryptoMetrics(cryptoData.length > 0 ? cryptoData.slice(0,6) : []);
        } else {
          setHistoricalSystemData([]);
          setSystemMetrics(null);
          setHistoricalCryptoData([]);
          setCryptoMetrics(null);
        }
      } catch (error) {
        console.error('Error fetching metrics:', error);
      }
    };
    fetchData();
    const intervalId = setInterval(fetchData, 5000); // Fetch every 5 seconds

    return () => clearInterval(intervalId);
  }, [selectedMetricName]);

  console.log('Historical Crypto Data:', historicalCryptoData);
  console.log('Crypto Metrics:', cryptoMetrics);  
  console.log('Historical System Data:', historicalSystemData);
  console.log('System Metrics:', systemMetrics);

  function formatOffset(offset) {
    // Handle zero offset
    if (offset === 0) return '+00:00';
    
    // Convert offset to hours and minutes
    const hours = Math.floor(Math.abs(offset) / 60);
    const minutes = Math.abs(offset) % 60;
    
    // Format the string with proper sign and padding
    return `${offset > 0 ? '+' : '-'}${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
  }

  function formatTimestamp(timestamp_utc, utc_offset) {
    try {
      // Parse the timestamp and add 'Z' to indicate UTC
      const date = new Date(timestamp_utc + 'Z');
      return date.toISOString().replace('T', ' ').substring(0, 19) + formatOffset(utc_offset);
    } catch (error) {
      console.error('Error formatting timestamp:', error);
      return 'Invalid timestamp';
    }
  }
  return (
    <Router basename="/Device-Dashboard">
      <HeaderBanner>Device Dashboard</HeaderBanner>
    
        
      <div style={{padding: '10px'}}>
        <GaugeContainer>
          <MetricHeading>{selectedMetricName}</MetricHeading>
        <Gauge value={selectedMetricValue} />
        <ChoiceContainer>
        {systemMetrics.length > 0 && (
          systemMetrics.map((metric) => (
            metric.unit === '%' && <Button key={metric.name} onClick={() => {setSelectedMetricValue(metric.value); setSelectedMetricName(metric.name)}}>{metric.name}</Button>
          ))
        )}
        </ChoiceContainer>
        </GaugeContainer>

  <MetricHeading>Latest System Metrics</MetricHeading>
  {systemMetrics && systemMetrics.length > 0 ? (
    <div>
      <p>Device: {systemMetrics[0].deviceName}</p>
      <p>Time: {formatTimestamp(systemMetrics[0].timestamp_utc, systemMetrics[0].utc_offset)}</p>
      {systemMetrics.map((metric) => (
        <p key={metric.name}>{metric.name}: {metric.value} {metric.unit}</p>
      ))}
    </div>
  ) : (
    <p>No system metrics available.</p>
  )}

  <h3>System Metrics History</h3>
  <Button onClick={toggleSystemTable}>
    {showSystemTable ? 'Hide History' : 'Show History'}
  </Button>
  {showSystemTable && (
    <TableContainer>
    <StyledTable>
      <TableHeader>
        <TableHeaderRow>
          <TableHeaderCell>Device</TableHeaderCell>
          <TableHeaderCell>Metric</TableHeaderCell>
          <TableHeaderCell>Value</TableHeaderCell>
          <TableHeaderCell>Timestamp</TableHeaderCell>
        </TableHeaderRow>
      </TableHeader>
      <TableBody>
        {historicalSystemData.length > 0 ? (
          historicalSystemData.map((metric, index) => (
            <TableRow key={index} className={index % 2 === 0 ? '' : 'active-row'}>
              <TableCell>{metric.deviceName}</TableCell>
              <TableCell>{metric.name}</TableCell>
              <TableCell>{metric.value}{metric.unit}</TableCell>
              <TableCell>{formatTimestamp(metric.timestamp_utc, metric.utc_offset)}</TableCell>
            </TableRow>
          ))
        ) : (
          <TableRow>
            <TableCell colSpan="4">No historical system data available.</TableCell>
          </TableRow>
        )}
      </TableBody>
    </StyledTable>
    </TableContainer>
  )}
</div>

<div style={{padding: '10px'}}>
  <MetricHeading>Latest Crypto Metrics</MetricHeading>
  {cryptoMetrics && cryptoMetrics.length > 0 ? (
    <div>
      <p>Device: {cryptoMetrics[0].deviceName}</p>
      <p>Time: {formatTimestamp(cryptoMetrics[0].timestamp_utc, cryptoMetrics[0].utc_offset)}</p>
      {cryptoMetrics.map((metric) => (
        <p key={metric.name}>{metric.name}: {getSymbolFromCurrency(metric.unit)}{metric.value}</p>
      ))}
    </div>
  ) : (
    <p>No crypto metrics available.</p>
  )}

<h3>Crypto Price History</h3>
  <Button onClick={toggleCryptoTable}>
    {showCryptoTable ? 'Hide History' : 'Show History'}
  </Button>

  {showCryptoTable && (
            <TableContainer>
              <StyledTable>
                <TableHeader>
                  <TableHeaderRow>
                    <TableHeaderCell>Currency</TableHeaderCell>
                    <TableHeaderCell>Metric</TableHeaderCell>
                    <TableHeaderCell>Value</TableHeaderCell>
                    <TableHeaderCell>Timestamp</TableHeaderCell>
                  </TableHeaderRow>
                </TableHeader>
                <TableBody>
                  {historicalCryptoData.length > 0 ? (
                    historicalCryptoData.map((metric, index) => (
                      <TableRow key={index} className={index % 2 === 0 ? '' : 'active-row'}>
                        <TableCell>{metric.deviceName}</TableCell>
                        <TableCell>{metric.name}</TableCell>
                        <TableCell>{getSymbolFromCurrency(metric.unit)}{metric.value}</TableCell>
                        <TableCell>{formatTimestamp(metric.timestamp_utc, metric.utc_offset)}</TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan="4">No historical crypto data available.</TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </StyledTable>
              </TableContainer>


  )}

          <Chart cryptoData={historicalCryptoData} />
        </div>
    </Router>
  );
}

export default App;