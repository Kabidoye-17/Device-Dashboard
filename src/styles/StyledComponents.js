import styled from 'styled-components';
import { Link as RouterLink } from 'react-router-dom';

export const Container = styled.div`
  padding: 5px;
  width: 100%
`;

export const GaugeContainer = styled.div`
  width: 100%;
  height: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
`;

export const ChoiceContainer = styled.div`
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: row;
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
  transition: background 0.3s ease, transform 0.2s ease;
  &:hover {
    background: #0056b3;
    transform: scale(1.05);
  }
  &:active {
    background: #004494;
    transform: scale(0.95);
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

export const HeaderBanner = styled.div`
  color: white;
  background:  #009879;
  height: 150px;	
  font-size: 40px;
  font-weight: bold;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
`;

export const MetricHeading = styled.div`
  color: black;
  font-size: 32px;
  font-weight: bold;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100px;	
`;

/* CSS */
export const Button = styled.button`
  background: #009879;
  border-radius: 999px;
  box-shadow: rgb(1, 71, 57) 0 10px 20px -10px;
  box-sizing: border-box;
  color: #FFFFFF;
  cursor: pointer;
  font-size: 16px;
  font-weight: 700;
  line-height: 24px;
  opacity: 1;
  outline: 0 solid transparent;
  padding: 8px 18px;
  margin-bottom: 10px;
  margin-right: 2px;
  user-select: none;
  -webkit-user-select: none;
  touch-action: manipulation;
  width: fit-content;
  word-break: break-word;
  border: 0;
  transition: background 0.3s ease, transform 0.2s ease;
  &:hover {
    background: #007bff;
    transform: scale(1.05);
  }
  &:active {
    background: #0056b3;
    transform: scale(0.95);
  }
`;
