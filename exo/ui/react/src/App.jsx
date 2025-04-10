import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import AnimatedDot from './components/AnimatedDot';
import ChatWindow from './components/ChatWindow';
import TitleBar from './components/TitleBar';

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  background-color: var(--background-color);
`;

const MainContent = styled.div`
  display: flex;
  flex-direction: column;
  flex: 1;
  padding: 16px;
  position: relative;
`;

function App() {
  const [messages, setMessages] = useState([]);
  const [dotState, setDotState] = useState('idle');
  
  // Handle messages from the backend
  useEffect(() => {
    // Check if we're running in Electron
    if (window.api) {
      window.api.receive('from-backend', (data) => {
        console.log('Received from backend:', data);
        
        if (data.type === 'message') {
          // Add the message to the chat
          setMessages((prevMessages) => [...prevMessages, data.message]);
        } else if (data.type === 'dot_state') {
          // Update the dot state
          setDotState(data.state);
        }
      });
    }
  }, []);
  
  // Send a message to the backend
  const sendMessage = (text) => {
    const message = {
      role: 'user',
      content: text,
      timestamp: Date.now()
    };
    
    // Add the message to the chat
    setMessages((prevMessages) => [...prevMessages, message]);
    
    // Send the message to the backend
    if (window.api) {
      window.api.send('to-backend', {
        type: 'message',
        message
      });
    }
    
    // For demo purposes, simulate a response
    setTimeout(() => {
      const response = {
        role: 'assistant',
        content: `I received your message: "${text}"`,
        timestamp: Date.now()
      };
      
      setMessages((prevMessages) => [...prevMessages, response]);
    }, 1000);
  };
  
  return (
    <AppContainer>
      <TitleBar />
      <MainContent>
        <AnimatedDot state={dotState} />
        <ChatWindow messages={messages} onSendMessage={sendMessage} />
      </MainContent>
    </AppContainer>
  );
}

export default App;
