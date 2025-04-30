import React from 'react';
import { Box, Paper, Typography, Avatar } from '@mui/material';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';

const ChatMessageList = ({ messages }) => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {messages.map((message) => (
        <Box
          key={message.id}
          sx={{
            display: 'flex',
            alignItems: 'flex-start',
            gap: 1,
            flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
            mb: 2,
          }}
        >
          {/* Avatar */}
          <Avatar
            sx={{
              bgcolor: message.role === 'assistant' ? 'primary.main' : 'secondary.main',
            }}
          >
            {message.role === 'assistant' ? <SmartToyIcon fontSize="small" /> : <PersonIcon fontSize="small" />}
          </Avatar>

          {/* Message Content */}
          <Paper
            variant="outlined"
            sx={{
              p: 2,
              maxWidth: '85%',
              borderRadius: 2,
              bgcolor: message.role === 'assistant' ? 'background.paper' : 'primary.dark',
              ml: message.role === 'user' ? 'auto' : 0,
              mr: message.role === 'assistant' ? 'auto' : 0,
            }}
          >
            <Typography variant="body2">{message.content}</Typography>
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ display: 'block', mt: 1, textAlign: message.role === 'user' ? 'right' : 'left' }}
            >
              {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </Typography>
          </Paper>
        </Box>
      ))}
    </Box>
  );
};

export default ChatMessageList;