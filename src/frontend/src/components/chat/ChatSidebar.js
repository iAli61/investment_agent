import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  Typography, 
  Avatar, 
  CircularProgress
} from '@mui/material';
import ChatMessageList from './ChatMessageList';
import ChatInput from './ChatInput';
import apiService from '../../services/api';

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
  // Conversation context from backend
  const [context, setContext] = useState({});
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
    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);

    try {
      // Send message to backend AI conversation endpoint with context
      const result = await apiService.sendMessage(message, context);
      const assistantMessage = {
        id: userMessage.id + 1,
        role: 'assistant',
        content: result.response || 'I\'m sorry, I couldn\'t process that request.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);
      // Update context for next calls
      if (result.context) setContext(result.context);
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
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
        <ChatInput onSendMessage={handleSendMessage} loading={isTyping} />
      </Box>
    </Box>
  );
};

export default ChatSidebar;