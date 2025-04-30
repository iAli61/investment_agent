import React, { useState } from 'react';
import { Container, Box, Typography } from '@mui/material';
import ChatInterface from '../components/chat/ChatInterface';

/**
 * Chat page component that provides the AI assistant interface
 */
const ChatPage = () => {
  const [context, setContext] = useState({
    // Initial context values if needed
    // property_id: null,
    // scenario_id: null,
  });

  const handleContextUpdate = (newContext) => {
    setContext(prevContext => ({
      ...prevContext,
      ...newContext
    }));
  };

  return (
    <Container maxWidth="lg" sx={{ py: 3, height: 'calc(100vh - 64px)' }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight="bold">
          AI Investment Assistant
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Ask questions about property investment, get real-time analysis, and receive personalized advice
        </Typography>
      </Box>
      
      <Box sx={{ height: 'calc(100% - 80px)' }}>
        <ChatInterface 
          context={context}
          onContextUpdate={handleContextUpdate}
          useStreaming={true}
        />
      </Box>
    </Container>
  );
};

export default ChatPage;