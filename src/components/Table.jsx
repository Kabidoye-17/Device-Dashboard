import React from 'react';
import styled from 'styled-components';

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

const PaginationContainer = styled.div`
  display: flex;
  justify-content: center;
  margin-top: 10px;
`;

const PaginationButton = styled.button`
  background-color: #009879;
  color: white;
  border: none;
  padding: 10px;
  margin: 0 5px;
  cursor: pointer;
  border-radius: 5px;

  &:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
  }
`;

const Table = ({ data, columns, formatTimestamp, getSymbolFromCurrency, currentPage, totalPages, onPageChange }) => (
  <TableContainer>
    <StyledTable>
      <TableHeader>
        <TableHeaderRow>
          {columns.map((column, index) => (
            <TableHeaderCell key={index}>{column}</TableHeaderCell>
          ))}
        </TableHeaderRow>
      </TableHeader>
      <TableBody>
        {data.length > 0 ? (
          data.map((metric, index) => (
            <TableRow key={index} className={index % 2 === 0 ? '' : 'active-row'}>
              <TableCell>{metric.deviceName}</TableCell>
              <TableCell>{metric.name}</TableCell>
              <TableCell>{getSymbolFromCurrency ? getSymbolFromCurrency(metric.unit) : ''}{metric.value}</TableCell>
              <TableCell>{formatTimestamp(metric.timestamp_utc, metric.utc_offset)}</TableCell>
            </TableRow>
          ))
        ) : (
          <TableRow>
            <TableCell colSpan={columns.length}>No data available.</TableCell>
          </TableRow>
        )}
      </TableBody>
    </StyledTable>
    <PaginationContainer>
      <PaginationButton onClick={() => onPageChange(currentPage - 1)} disabled={currentPage === 0}>
        Previous
      </PaginationButton>
      <PaginationButton onClick={() => onPageChange(currentPage + 1)} disabled={currentPage >= totalPages - 1 || totalPages === 0}>
        Next
      </PaginationButton>
    </PaginationContainer>
  </TableContainer>
);

export default Table;
