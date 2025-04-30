import React, { useState } from 'react';
import { 
  Box, 
  TextField, 
  IconButton, 
  Paper,
  InputAdornment,
  Tooltip
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import MicIcon from '@mui/icons-material/Mic';
import ClearIcon from '@mui/icons-material/Clear';

/**
 * Chat input component with send button
 * 
 * @param {Object} props Component props
 * @param {Function} props.onSendMessage Callback when message is sent
 * @param {boolean} props.disabled Whether the input is disabled
 * @param {boolean} props.loading Whether system is processing a message
 */
const ChatInput = ({ onSendMessage, disabled = false, loading = false }) => {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (message.trim() && !disabled && !loading) {
      onSendMessage(message);
      setMessage('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClear = () => {
    setMessage('');
  };

  return (
    <Paper
      elevation={2}
      sx={{
        p: 1.5,
        borderRadius: 3,
        bgcolor: 'background.paper',
        width: '100%'
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'flex-end' }}>
        <TextField
          fullWidth
          multiline
          maxRows={4}
          placeholder="Ask about property investment analysis..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={disabled || loading}
          variant="standard"
          sx={{
            '& .MuiInputBase-root': {
              px: 2,
              py: 1,
              fontSize: '1rem',
            },
            '& .MuiInput-underline:before': { borderBottom: 'none' },
            '& .MuiInput-underline:after': { borderBottom: 'none' },
            '& .MuiInput-underline:hover:not(.Mui-disabled):before': { borderBottom: 'none' },
          }}
          InputProps={{
            endAdornment: message && (
              <InputAdornment position="end">
                <IconButton
                  aria-label="clear message"
                  onClick={handleClear}
                  edge="end"
                  size="small"
                >
                  <ClearIcon fontSize="small" />
                </IconButton>
              </InputAdornment>
            ),
          }}
        />

        <Box sx={{ display: 'flex', ml: 1 }}>
          <Tooltip title="Voice input (coming soon)">
            <span>
              <IconButton
                color="primary"
                sx={{ mx: 0.5 }}
                disabled={true} // Voice input not implemented yet
              >
                <MicIcon />
              </IconButton>
            </span>
          </Tooltip>

          <Tooltip title="Send message">
            <span>
              <IconButton
                color="primary"
                onClick={handleSend}
                disabled={!message.trim() || disabled || loading}
                sx={{
                  bgcolor: 'primary.main',
                  color: 'white',
                  '&:hover': {
                    bgcolor: 'primary.dark',
                  },
                  '&.Mui-disabled': {
                    bgcolor: 'action.disabledBackground',
                  }
                }}
              >
                <SendIcon />
              </IconButton>
            </span>
          </Tooltip>
        </Box>
      </Box>
    </Paper>
  );
};

export default ChatInput;