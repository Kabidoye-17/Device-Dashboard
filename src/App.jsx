import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { HeaderBanner, MetricHeading, Button, GaugeContainer, ChoiceContainer } from './styles/StyledComponents';
import { apiUrl } from './config';
import getSymbolFromCurrency from 'currency-symbol-map';
import Gauge from './components/Gauge';
import Chart from './components/Chart';
import Table from './components/Table';

function App() {
  const [historicalCryptoData, setHistoricalCryptoData] = useState([]);
  const [cryptoMetrics, setCryptoMetrics] = useState([]);
  const [historicalSystemData, setHistoricalSystemData] = useState([]);
  const [systemMetrics, setSystemMetrics] = useState([]);
  const [showSystemTable, setShowSystemTable] = useState(false);
  const [showCryptoTable, setShowCryptoTable] = useState(false);
  const [selectedMetricValue, setSelectedMetricValue] = useState();
  const [selectedMetricName, setSelectedMetricName] = useState();
  const [currentCryptoPage, setCurrentCryptoPage] = useState(0);
  const [currentSystemPage, setCurrentSystemPage] = useState(0);
  const [totalCryptoPages, setTotalCryptoPages] = useState(0);
  const [totalSystemPages, setTotalSystemPages] = useState(0);
  const [selectedDevice, setSelectedDevice] = useState('');
  const [availableDevices, setAvailableDevices] = useState([]);
  const [cryptoGraphData, setCryptoGraphData] = useState([]);

  const toggleSystemTable = () => {
    setShowSystemTable(!showSystemTable);
    setCurrentSystemPage(0);
  };

  const toggleCryptoTable = () => {
    setShowCryptoTable(!showCryptoTable);
    setCurrentCryptoPage(0);
  };

  const handleDeviceChange = (event) => {
    const newDevice = event.target.value;
    setSelectedDevice(newDevice);

    const deviceMetrics = systemMetrics.filter(metric => metric.deviceName === newDevice);
    const firstPercentageMetric = deviceMetrics.find(metric => metric.unit === '%');
    if (firstPercentageMetric) {
      setSelectedMetricValue(firstPercentageMetric.value);
      setSelectedMetricName(firstPercentageMetric.name);
    }
  };

  const formatData = (data) => {
    if (!Array.isArray(data)) {
      console.error('Expected data to be an array, but got:', data);
      return [];
    }
    return data.map(item => ({
      deviceName: item.device_name,
      name: item.name,
      value: item.value,
      unit: item.unit,
      timestamp_utc: item.timestamp_utc,
      utc_offset: item.utc_offset,
      type: item.type
    }));
  };

  const updateGaugeMetric = (formattedLatestData) => {
    const firstPercentageMetric = formattedLatestData.find(metric => metric.unit === '%');
    if (!selectedMetricName && firstPercentageMetric) {
      setSelectedMetricValue(firstPercentageMetric.value);
      setSelectedMetricName(firstPercentageMetric.name);
    } else if (selectedMetricName) {
      const updatedMetric = formattedLatestData.find(metric => metric.name === selectedMetricName);
      if (updatedMetric) {
        setSelectedMetricValue(updatedMetric.value);
      }
    }
  };

  const fetchSystemData = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/metrics/get-latest-metrics?metric_type=system&page_number=${currentSystemPage + 1}`);
      const data = await response.json();
      const allPaginatedData = data.metrics;
      const latestMetrics = data.latest_metric;
      const totalPages = data.total_pages;

      setTotalSystemPages(totalPages || 0);

      if (allPaginatedData && allPaginatedData.length > 0) {
        const formattedPaginatedData = formatData(allPaginatedData);
        const formattedLatestData = formatData(latestMetrics);

        const metricOrder = {
          'CPU Load': 1,
          'RAM Usage': 2,
          'Network Sent': 3
        };

        const systemData = formattedPaginatedData
          .filter(item => item.type === 'system')
          .sort((a, b) => {
            const timeCompare = new Date(b.timestamp_utc) - new Date(a.timestamp_utc);
            if (timeCompare !== 0) return timeCompare;
            return metricOrder[a.name] - metricOrder[b.name];
          });

        updateGaugeMetric(formattedLatestData);

        const uniqueDevices = [...new Set(formattedLatestData.map(metric => metric.deviceName))];
        setAvailableDevices(uniqueDevices);
        if (!selectedDevice && uniqueDevices.length > 0) {
          setSelectedDevice(uniqueDevices[0]);
        }

        setHistoricalSystemData(systemData);
        setSystemMetrics(formattedLatestData);
      } else {
        setHistoricalSystemData([]);
        setSystemMetrics(null);
      }
    } catch (error) {
      console.error('Error fetching system metrics:', error);
    }
  };

  const fetchCryptoData = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/metrics/get-latest-metrics?metric_type=crypto&page_number=${currentCryptoPage + 1}`);
      const data = await response.json();
      const allPaginatedData = data.metrics;
      const latestMetrics = data.latest_metric;
      const totalPages = data.total_pages;

      setTotalCryptoPages(totalPages || 0);

      if (allPaginatedData && allPaginatedData.length > 0) {
        const formattedPaginatedData = formatData(allPaginatedData);
        const formattedLatestData = formatData(latestMetrics);

        const cryptoOrder = {
          'ETH': 1,
          'BTC': 2
        };

        const cryptoMetricOrder = {
          'Price': 1,
          'Ask': 2,
          'Bid': 3
        };

        const cryptoData = formattedPaginatedData
          .filter(item => item.type === 'crypto')
          .sort((a, b) => {
            const timeCompare = new Date(b.timestamp_utc) - new Date(a.timestamp_utc);
            if (timeCompare !== 0) return timeCompare;

            const currencyA = a.name.split('-')[0];
            const currencyB = b.name.split('-')[0];

            if (currencyA !== currencyB) {
              return cryptoOrder[currencyA] - cryptoOrder[currencyB];
            }

            const metricA = a.name.split(' ')[1];
            const metricB = b.name.split(' ')[1];

            return cryptoMetricOrder[metricA] - cryptoMetricOrder[metricB];
          });

        updateGaugeMetric(formattedLatestData);

        setHistoricalCryptoData(cryptoData);
        setCryptoMetrics(formattedLatestData);

        setCryptoGraphData(prevData => {
          const newData = formattedLatestData.filter(metric => 
            !prevData.some(prevMetric => prevMetric.timestamp_utc === metric.timestamp_utc)
          );
          const combinedData = [...prevData, ...newData];
          const latestData = combinedData.slice(-60); // Keep only the latest 30 metrics (10 sets of Price, Ask, Bid)
          return latestData;
        });
      } else {
        setHistoricalCryptoData([]);
        setCryptoMetrics(null);
      }
    } catch (error) {
      console.error('Error fetching crypto metrics:', error);
    }
  };

  useEffect(() => {
    fetchSystemData();
    const intervalId = setInterval(fetchSystemData, 2000);

    return () => clearInterval(intervalId);
    // eslint-disable-next-line
  }, [selectedMetricName, currentSystemPage]);

  useEffect(() => {
    fetchCryptoData();
    const intervalId = setInterval(fetchCryptoData, 2000);

    return () => clearInterval(intervalId);
    // eslint-disable-next-line
  }, [currentCryptoPage]);

  useEffect(() => {
    console.log('Total System Pages:', totalSystemPages);
    console.log('Current System Page:', currentSystemPage);
  }, [totalSystemPages, currentSystemPage]);

  useEffect(() => {
    console.log('Total Crypto Pages:', totalCryptoPages);
    console.log('Current Crypto Page:', currentCryptoPage);
  }, [totalCryptoPages, currentCryptoPage]);

  const formatOffset = (offset) => {
    if (offset === 0) return '+00:00';

    const hours = Math.floor(Math.abs(offset) / 60);
    const minutes = Math.abs(offset) % 60;

    return `${offset > 0 ? '+' : '-'}${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
  };

  const formatTimestamp = (timestamp_utc, utc_offset) => {
    try {
      const date = new Date(timestamp_utc + 'Z');
      return date.toISOString().replace('T', ' ').substring(0, 19) + formatOffset(utc_offset);
    } catch (error) {
      console.error('Error formatting timestamp:', error);
      return 'Invalid timestamp';
    }
  };

  return (
    <Router basename="/Device-Dashboard">
      <HeaderBanner>Device Dashboard</HeaderBanner>
      <div style={{ padding: '10px' }}>
        <label htmlFor="device-select">Select Device:</label>
        <select id="device-select" value={selectedDevice} onChange={handleDeviceChange}>
          {availableDevices.map((device) => (
            <option key={device} value={device}>{device}</option>
          ))}
        </select>
        <GaugeContainer>
          <MetricHeading>{selectedMetricName}</MetricHeading>
          <Gauge value={selectedMetricValue} />
          <ChoiceContainer>
            {systemMetrics.length > 0 &&
              systemMetrics.filter(metric => metric.deviceName === selectedDevice).map((metric) => (
                metric.unit === '%' && <Button key={metric.name} onClick={() => { setSelectedMetricValue(metric.value); setSelectedMetricName(metric.name); }}>{metric.name}</Button>
              ))}
          </ChoiceContainer>
        </GaugeContainer>

        <MetricHeading>Latest System Metrics</MetricHeading>
        {systemMetrics && systemMetrics.length > 0 ? (
          <div>
            <p>Device: {selectedDevice}</p>
            <p>Time: {formatTimestamp(systemMetrics[0].timestamp_utc, systemMetrics[0].utc_offset)}</p>
            {systemMetrics.filter(metric => metric.deviceName === selectedDevice).map((metric) => (
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
          <Table
            data={historicalSystemData.filter(metric => metric.deviceName === selectedDevice)}
            columns={['Device', 'Metric', 'Value', 'Timestamp']}
            formatTimestamp={formatTimestamp}
            currentPage={currentSystemPage}
            totalPages={totalSystemPages}
            onPageChange={setCurrentSystemPage}
          />
        )}
      </div>

      <div style={{ padding: '10px' }}>
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
          <Table
            data={historicalCryptoData}
            columns={['Currency', 'Metric', 'Value', 'Timestamp']}
            formatTimestamp={formatTimestamp}
            getSymbolFromCurrency={getSymbolFromCurrency}
            currentPage={currentCryptoPage}
            totalPages={totalCryptoPages}
            onPageChange={setCurrentCryptoPage}
          />
        )}

        <Chart cryptoData={cryptoGraphData} />
      </div>
    </Router>
  );
}

export default App;