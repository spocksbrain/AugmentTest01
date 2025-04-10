import React from 'react';
import styled from 'styled-components';

const TitleBarContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 32px;
  background-color: var(--background-color);
  padding: 0 16px;
  -webkit-app-region: drag;
`;

const Title = styled.div`
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary-color);
`;

const WindowControls = styled.div`
  display: flex;
  -webkit-app-region: no-drag;
`;

const WindowButton = styled.button`
  width: 16px;
  height: 16px;
  border-radius: 50%;
  margin-left: 8px;
  border: none;
  outline: none;
  cursor: pointer;
`;

const CloseButton = styled(WindowButton)`
  background-color: #ff5f56;
  
  &:hover {
    background-color: #ff3333;
  }
`;

const MinimizeButton = styled(WindowButton)`
  background-color: #ffbd2e;
  
  &:hover {
    background-color: #ffaa00;
  }
`;

const MaximizeButton = styled(WindowButton)`
  background-color: #27c93f;
  
  &:hover {
    background-color: #00cc00;
  }
`;

const TitleBar = () => {
  const handleClose = () => {
    if (window.api) {
      window.api.send('to-backend', { type: 'window_control', action: 'close' });
    }
  };
  
  const handleMinimize = () => {
    if (window.api) {
      window.api.send('to-backend', { type: 'window_control', action: 'minimize' });
    }
  };
  
  const handleMaximize = () => {
    if (window.api) {
      window.api.send('to-backend', { type: 'window_control', action: 'maximize' });
    }
  };
  
  return (
    <TitleBarContainer>
      <Title>exo</Title>
      <WindowControls>
        <MinimizeButton onClick={handleMinimize} />
        <MaximizeButton onClick={handleMaximize} />
        <CloseButton onClick={handleClose} />
      </WindowControls>
    </TitleBarContainer>
  );
};

export default TitleBar;
