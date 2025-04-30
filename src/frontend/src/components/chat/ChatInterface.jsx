import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  TextField, 
  Typography, 
  Paper, 
  CircularProgress,
  IconButton
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import MarkdownView from '../common/MarkdownView';
import apiService from '../../services/api';

/**
 * Chat interface component for interacting with the AI assistant
 * @param {Object} props - Component props
 * @param {Object} props.context - Context information for the conversation
 * @param {Function} props.onContextUpdate - Callback to update context
 * @param {boolean} props.useStreaming - Whether to use streaming for responses
 */
const ChatInterface = ({ context, onContextUpdate, useStreaming = false }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [streamedResponse, setStreamedResponse] = useState('');
  const [eventSource, setEventSource] = useState(null);
  const messagesEndRef = useRef(null);

  // Cleanup event source on unmount
  useEffect(() => {
    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [eventSource]);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamedResponse]);

  /**
   * Send a message to the AI assistant
   */
  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');
    
    // Add user message to chat
    setMessages(prevMessages => [
      ...prevMessages, 
      { role: 'user', content: userMessage }
    ]);

    setIsLoading(true);

    try {
      if (useStreaming) {
        // Use streaming approach
        await handleStreamingResponse(userMessage);
      } else {
        // Use standard request/response
        await handleStandardResponse(userMessage);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prevMessages => [
        ...prevMessages,
        { 
          role: 'assistant', 
          content: 'Sorry, I encountered an error processing your request. Please try again.'
        }
      ]);
      setIsLoading(false);
    }
  };

  /**
   * Handle streaming response from the AI assistant
   * @param {string} userMessage - User's message
   */
  const handleStreamingResponse = async (userMessage) => {
    // Reset streamed response
    setStreamedResponse('');
    
    // Create temporary message for streaming
    setMessages(prevMessages => [
      ...prevMessages,
      { role: 'assistant', content: '', isStreaming: true }
    ]);

    try {
      // Close any existing EventSource
      if (eventSource) {
        eventSource.close();
      }

      // Get streaming response using the updated API service
      const { eventSource: newEventSource, postPromise } = apiService.streamConversation(
        userMessage, 
        context
      );

      // Store the event source for cleanup
      setEventSource(newEventSource);

      // Wait for POST request to complete
      await postPromise;

      // Listen for events
      newEventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'content') {
            setStreamedResponse(prev => prev + (data.data || ''));
          }

          // If done, clean up
          if (data.done) {
            newEventSource.close();
            setEventSource(null);
            setIsLoading(false);
            
            // Replace streaming message with complete message
            setMessages(prevMessages => {
              const updatedMessages = [...prevMessages];
              const lastIndex = updatedMessages.length - 1;
              if (lastIndex >= 0 && updatedMessages[lastIndex].isStreaming) {
                updatedMessages[lastIndex] = { 
                  role: 'assistant', 
                  content: streamedResponse + (data.data || '')
                };
              }
              return updatedMessages;
            });
            
            setStreamedResponse('');
          }
        } catch (error) {
          console.error('Error parsing SSE data:', error);
        }
      };

      newEventSource.onerror = (error) => {
        console.error('SSE error:', error);
        newEventSource.close();
        setEventSource(null);
        setIsLoading(false);
        
        // Update messages to show error
        setMessages(prevMessages => {
          const updatedMessages = [...prevMessages];
          const lastIndex = updatedMessages.length - 1;
          if (lastIndex >= 0 && updatedMessages[lastIndex].isStreaming) {
            updatedMessages[lastIndex] = { 
              role: 'assistant', 
              content: streamedResponse || 'Sorry, the connection was interrupted. Please try again.'
            };
          }
          return updatedMessages;
        });
        
        setStreamedResponse('');
      };
    } catch (error) {
      console.error('Error setting up streaming:', error);
      setIsLoading(false);
      
      // Update messages to show error
      setMessages(prevMessages => {
        const updatedMessages = [...prevMessages];
        const lastIndex = updatedMessages.length - 1;
        if (lastIndex >= 0 && updatedMessages[lastIndex].isStreaming) {
          updatedMessages[lastIndex] = { 
            role: 'assistant', 
            content: 'Sorry, I encountered an error processing your request. Please try again.'
          };
        }
        return updatedMessages;
      });
    }
  };

  /**
   * Handle standard (non-streaming) response from the AI assistant
   * @param {string} userMessage - User's message
   */
  const handleStandardResponse = async (userMessage) => {
    try {
      // Send message using the updated API service
      const response = await apiService.sendMessage(userMessage, context);
      
      // Add assistant message to chat
      setMessages(prevMessages => [
        ...prevMessages,
        { role: 'assistant', content: response.response }
      ]);
      
      // Update context if provided in response
      if (response.context && onContextUpdate) {
        onContextUpdate(response.context);
      }
    } catch (error) {
      console.error('Error in standard response:', error);
      setMessages(prevMessages => [
        ...prevMessages,
        { 
          role: 'assistant', 
          content: 'Sorry, I encountered an error processing your request. Please try again.'
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle key press to send message on Enter
   * @param {Object} event - Key press event
   */
  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column', 
      height: '100%', 
      backgroundColor: 'background.paper',
      borderRadius: 2,
      overflow: 'hidden',
      boxShadow: 3
    }}>
      {/* Chat Messages */}
      <Box sx={{ 
        flexGrow: 1, 
        overflowY: 'auto', 
        p: 2,
        display: 'flex',
        flexDirection: 'column',
        gap: 2
      }}>
        {messages.length === 0 && (
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            height: '100%',
            opacity: 0.7
          }}>
            <Typography variant="body1" color="text.secondary">
              Ask me anything about property investment and analysis
            </Typography>
          </Box>
        )}
        
        {messages.map((message, index) => (
          <Paper 
            key={index} 
            elevation={1}
            sx={{ 
              p: 2, 
              maxWidth: '80%', 
              alignSelf: message.role === 'user' ? 'flex-end' : 'flex-start',
              backgroundColor: message.role === 'user' ? 'primary.light' : 'background.default',
              color: message.role === 'user' ? 'primary.contrastText' : 'text.primary',
              borderRadius: 2
            }}
          >
            {message.role === 'user' ? (
              <Typography variant="body1">{message.content}</Typography>
            ) : (
              <MarkdownView content={message.content} />
            )}
          </Paper>
        ))}
        
        {/* Streaming response */}
        {streamedResponse && (
          <Paper 
            elevation={1}
            sx={{ 
              p: 2, 
              maxWidth: '80%', 
              alignSelf: 'flex-start',
              backgroundColor: 'background.default',
              borderRadius: 2
            }}
          >
            <MarkdownView content={streamedResponse} />
          </Paper>
        )}
        
        {/* Loading indicator */}
        {isLoading && !streamedResponse && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
            <CircularProgress size={24} />
          </Box>
        )}
        
        {/* Auto-scroll anchor */}
        <div ref={messagesEndRef} />
      </Box>
      
      {/* Input Area */}
      <Box sx={{ 
        p: 2, 
        borderTop: 1, 
        borderColor: 'divider',
        backgroundColor: 'background.default'
      }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Type your message..."
            multiline
            maxRows={4}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
            sx={{ 
              backgroundColor: 'background.paper',
              '& .MuiOutlinedInput-root': {
                borderRadius: 2
              }
            }}
          />
          <IconButton 
            color="primary"
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            sx={{ alignSelf: 'flex-end' }}
          >
            {isLoading ? <CircularProgress size={24} /> : <SendIcon />}
          </IconButton>
        </Box>
      </Box>
    </Box>
  );
};

export default ChatInterface;