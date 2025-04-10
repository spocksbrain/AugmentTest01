import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import ReactMarkdown from 'react-markdown';

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  background-color: var(--surface-color);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const InputContainer = styled.div`
  display: flex;
  padding: 16px;
  background-color: var(--background-color);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
`;

const Input = styled.input`
  flex: 1;
  padding: 12px 16px;
  border-radius: 24px;
  border: none;
  background-color: var(--surface-color);
  color: var(--text-primary-color);
  font-size: 16px;
  outline: none;
  
  &:focus {
    box-shadow: 0 0 0 2px var(--primary-color);
  }
`;

const SendButton = styled.button`
  margin-left: 8px;
  padding: 12px 16px;
  border-radius: 24px;
  border: none;
  background-color: var(--primary-color);
  color: white;
  font-size: 16px;
  cursor: pointer;
  outline: none;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: #7c4dff;
  }
  
  &:active {
    background-color: #5e35b1;
  }
  
  &:disabled {
    background-color: var(--text-disabled-color);
    cursor: not-allowed;
  }
`;

const Message = styled.div`
  display: flex;
  flex-direction: column;
  padding: 12px 16px;
  border-radius: 8px;
  max-width: 80%;
  
  ${({ role }) => role === 'user' ? `
    align-self: flex-end;
    background-color: var(--primary-color);
    color: white;
  ` : `
    align-self: flex-start;
    background-color: #2d2d2d;
    color: var(--text-primary-color);
  `}
`;

const MessageContent = styled.div`
  font-size: 16px;
  line-height: 1.5;
  
  /* Style markdown content */
  p {
    margin: 0 0 8px 0;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  code {
    background-color: rgba(0, 0, 0, 0.2);
    padding: 2px 4px;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
  }
  
  pre {
    background-color: rgba(0, 0, 0, 0.2);
    padding: 8px;
    border-radius: 4px;
    overflow-x: auto;
    margin: 8px 0;
    
    code {
      background-color: transparent;
      padding: 0;
    }
  }
`;

const ChatWindow = ({ messages = [], onSendMessage }) => {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);
  
  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const handleSend = () => {
    if (inputValue.trim()) {
      onSendMessage(inputValue);
      setInputValue('');
    }
  };
  
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };
  
  return (
    <ChatContainer>
      <MessagesContainer>
        {messages.map((message, index) => (
          <Message key={index} role={message.role}>
            <MessageContent>
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </MessageContent>
          </Message>
        ))}
        <div ref={messagesEndRef} />
      </MessagesContainer>
      
      <InputContainer>
        <Input
          type="text"
          placeholder="Type a message..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          className="non-draggable"
        />
        <SendButton
          onClick={handleSend}
          disabled={!inputValue.trim()}
          className="non-draggable"
        >
          Send
        </SendButton>
      </InputContainer>
    </ChatContainer>
  );
};

export default ChatWindow;
