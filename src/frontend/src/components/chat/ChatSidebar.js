import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  Typography, 
  Avatar, 
  Paper,
  Divider,
  CircularProgress
} from '@mui/material';
import ChatMessageList from './ChatMessageList';
import ChatInput from './ChatInput';

const ChatSidebar = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: "Hello! I'm here to help analyze your property investment opportunities. Would you like to start with a new property analysis?",
      timestamp: new Date(),
    }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to the bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle sending a new message
  const handleSendMessage = async (message) => {
    if (!message.trim()) return;
    
    // Add user message to chat
    const userMessage = {
      id: messages.length + 1,
      role: 'user',
      content: message,
      timestamp: new Date(),
    };
    setMessages([...messages, userMessage]);
    setIsTyping(true);

    try {
      // In a real implementation, this would call your backend API
      // For now, simulate a response with a timeout
      setTimeout(() => {
        let response;
        
        // Simple rule-based responses for demonstration
        if (message.toLowerCase().includes('analyze property') || message.toLowerCase().includes('new analysis')) {
          response = "Great! I'll help you analyze a property. Please provide the address.";
        } else if (message.toLowerCase().includes('123 main')) {
          response = "Great! I'll help you analyze 123 Main Street, Boston, MA. I see it's listed for $450,000. I'll gather the market data and rental estimates. Please see the dashboard for details.";
        } else if (message.toLowerCase().includes('rental') || message.toLowerCase().includes('rent')) {
          response = "Based on comparable properties, the potential monthly rent for this property is around $2,800. This is slightly above the area average.";
        } else if (message.toLowerCase().includes('market')) {
          response = "The market in this area is strong. Property values have increased 3.5% over the past 6 months, and rental demand is high with a vacancy rate of only 5%.";
        } else if (message.toLowerCase().includes('return') || message.toLowerCase().includes('roi')) {
          response = "The projected ROI for this property is 12.7%, with a Cap Rate of 5.2% and Cash-on-Cash Return of 8.4%. These are solid numbers for this market.";
        } else {
          response = "I understand. What specific information would you like to know about property investments?";
        }

        const assistantMessage = {
          id: messages.length + 2,
          role: 'assistant',
          content: response,
          timestamp: new Date(),
        };
        
        setMessages(prevMessages => [...prevMessages, assistantMessage]);
        setIsTyping(false);
      }, 1500);
    } catch (error) {
      console.error('Error sending message:', error);
      setIsTyping(false);
    }
  };

  return (
    <Box 
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        pt: 8, // Account for app bar height
      }}
    >
      {/* AI Assistant Header */}
      <Box 
        sx={{ 
          p: 2, 
          borderBottom: 1, 
          borderColor: 'divider',
          display: 'flex',
          alignItems: 'center',
          gap: 1,
        }}
      >
        <Avatar 
          sx={{ bgcolor: 'primary.main' }}
          alt="AI Assistant"
        >
          AI
        </Avatar>
        <Box>
          <Typography variant="subtitle1" fontWeight={600}>
            AI Assistant
          </Typography>
          <Typography 
            variant="caption" 
            color="success.main"
            sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
          >
            <Box 
              component="span" 
              sx={{ 
                width: 8, 
                height: 8, 
                borderRadius: '50%', 
                bgcolor: 'success.main',
                display: 'inline-block'
              }} 
            />
            Online
          </Typography>
        </Box>
      </Box>

      {/* Messages Container */}
      <Box 
        sx={{ 
          flex: 1, 
          overflowY: 'auto',
          p: 2,
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <ChatMessageList messages={messages} />
        
        {/* Typing indicator */}
        {isTyping && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, my: 1 }}>
            <CircularProgress size={16} />
            <Typography variant="caption">AI Assistant is typing...</Typography>
          </Box>
        )}
        <div ref={messagesEndRef} />
      </Box>

      {/* Message Input */}
      <Box 
        sx={{ 
          p: 2, 
          borderTop: 1, 
          borderColor: 'divider',
        }}
      >
        <ChatInput onSendMessage={handleSendMessage} />
      </Box>
    </Box>
  );
};

export default ChatSidebar;