import React from 'react';
import { Box, Avatar, Typography, Paper, Chip } from '@mui/material';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';

/**
 * Component to display a single chat message
 * 
 * @param {Object} props Component props
 * @param {string} props.text Message text content
 * @param {boolean} props.isUser Whether the message is from the user
 * @param {Array} props.suggestions Suggestion chips to display
 * @param {Function} props.onSuggestionClick Callback when a suggestion is clicked
 * @param {boolean} props.isLoading Whether the message is still loading
 */
const ChatMessage = ({ 
  text, 
  isUser, 
  suggestions = [], 
  onSuggestionClick,
  isLoading = false 
}) => {
  return (
    <Box 
      sx={{ 
        display: 'flex', 
        mb: 2,
        alignItems: 'flex-start',
        flexDirection: isUser ? 'row-reverse' : 'row'
      }}
    >
      {/* Avatar */}
      <Avatar 
        sx={{ 
          bgcolor: isUser ? 'primary.main' : 'secondary.main',
          mr: isUser ? 0 : 1.5,
          ml: isUser ? 1.5 : 0
        }}
      >
        {isUser ? <PersonIcon /> : <SmartToyIcon />}
      </Avatar>

      {/* Message Content */}
      <Paper
        elevation={1}
        sx={{
          p: 2,
          maxWidth: '70%',
          bgcolor: isUser ? 'primary.dark' : 'background.paper',
          borderRadius: 2,
          position: 'relative'
        }}
      >
        {isLoading ? (
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Box sx={{ 
              width: 12, 
              height: 12, 
              borderRadius: '50%', 
              bgcolor: 'grey.500',
              animation: 'pulse 1.5s infinite ease-in-out',
              mr: 1,
              '@keyframes pulse': {
                '0%': { opacity: 0.5 },
                '50%': { opacity: 1 },
                '100%': { opacity: 0.5 }
              }
            }} />
            <Box sx={{ 
              width: 12, 
              height: 12, 
              borderRadius: '50%', 
              bgcolor: 'grey.500',
              animation: 'pulse 1.5s infinite ease-in-out 0.2s',
              mr: 1
            }} />
            <Box sx={{ 
              width: 12, 
              height: 12, 
              borderRadius: '50%', 
              bgcolor: 'grey.500',
              animation: 'pulse 1.5s infinite ease-in-out 0.4s'
            }} />
          </Box>
        ) : (
          <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
            {text}
          </Typography>
        )}

        {/* Suggestions */}
        {!isUser && suggestions && suggestions.length > 0 && (
          <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {suggestions.map((suggestion, index) => (
              <Chip
                key={index}
                label={suggestion}
                size="small"
                onClick={() => onSuggestionClick && onSuggestionClick(suggestion)}
                clickable
                color="primary"
                variant="outlined"
              />
            ))}
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default ChatMessage;