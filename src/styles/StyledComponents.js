import styled from 'styled-components';
import { Link as RouterLink } from 'react-router-dom';

export const Container = styled.div`
  padding: 20px;
`;

export const Navigation = styled.nav`
  margin-bottom: 20px;
`;

export const NavList = styled.ul`
  display: flex;
  gap: 20px;
  list-style: none;
  padding: 0;
`;

export const Link = styled(RouterLink)`
  text-decoration: none;
  color: #007bff;
  &:hover {
    text-decoration: underline;
  }
`;

export const ErrorContainer = styled.div`
  color: red;
  text-align: center;
  padding: 20px;
`;

export const RetryButton = styled.button`
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  &:hover {
    background: #0056b3;
  }
`;

export const GridContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
`;

export const Card = styled.div`
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  margin: 10px;
`;

export const MetricsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
`;
