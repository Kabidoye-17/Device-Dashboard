import React from 'react';
import styled from 'styled-components';

const FullScreenOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 9999;
`;

const Spinner = styled.div`
  border: 16px solid #f3f3f3;
  border-top: 16px solid #3498db;
  border-radius: 50%;
  width: 120px;
  height: 120px;
  animation: spin 2s linear infinite;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const Message = styled.div`
  margin-top: 20px;
  color: white;
  font-size: 24px;
  text-align: center;
`;

const Loading = () => (
  <FullScreenOverlay>
    <Spinner />
    <Message>Thanks for waiting...</Message>
  </FullScreenOverlay>
);

export default Loading;
