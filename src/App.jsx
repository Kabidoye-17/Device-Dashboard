import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SystemMetrics from './pages/SystemMetrics';
import CryptoPrices from './pages/CryptoPrices';
import { Container, Navigation, NavList, Link } from './styles/StyledComponents';

function App() {
  return (
    <Router>
      <Container>
        <Navigation>
          <NavList>
            <li>
              <Link to="/">System Metrics</Link>
            </li>
            <li>
              <Link to="/crypto">Crypto Prices</Link>
            </li>
          </NavList>
        </Navigation>

        <Routes>
          <Route path="/" element={<SystemMetrics />} />
          <Route path="/crypto" element={<CryptoPrices />} />
        </Routes>
      </Container>
    </Router>
  );
}

export default App;