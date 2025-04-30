import React, { useState } from 'react';
import { 
  Box, 
  TextField, 
  IconButton, 
  Chip,
  Tooltip,
  CircularProgress
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import MicIcon from '@mui/icons-material/Mic';
import AttachFileIcon from '@mui/icons-material/AttachFile';

/**
 * Enhanced ChatInput component with suggested actions and voice input
 */
const ChatInput = ({ onSendMessage, isProcessing, suggestedActions = [] }) => {
  const [input, setInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isProcessing) return;
    
    onSendMessage(input);
    setInput('');
  };

  const handleSuggestedAction = (action) => {
    onSendMessage(action);
  };

  const toggleVoiceRecording = () => {
    // This would connect to a speech-to-text service in a real implementation
    setIsRecording(!isRecording);
    
    if (isRecording) {
      // Simulate ending recording and getting text
      setTimeout(() => {
        setInput(prev => prev + " I'm interested in this property.");
        setIsRecording(false);
      }, 1500);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ 
      p: 2, 
      borderTop: '1px solid',
      borderColor: 'divider',
      bgcolor: 'background.paper',
      borderRadius: '0 0 12px 12px'
    }}>
      {/* Suggested Actions */}
      {suggestedActions.length > 0 && (
        <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {suggestedActions.map((action, index) => (
            <Chip
              key={index}
              label={action}
              variant="outlined"
              color="primary"
              onClick={() => handleSuggestedAction(action)}
              sx={{ borderRadius: '16px' }}
            />
          ))}
        </Box>
      )}
      
      {/* Input Field with Action Buttons */}
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        <Tooltip title="Attach document">
          <IconButton color="primary" sx={{ mr: 1 }}>
            <AttachFileIcon />
          </IconButton>
        </Tooltip>
        
        <TextField
          fullWidth
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about this property or type an address..."
          variant="outlined"
          size="medium"
          disabled={isProcessing}
          multiline
          maxRows={4}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: '24px',
              backgroundColor: 'background.default',
              '&.Mui-focused': {
                boxShadow: '0 0 0 2px rgba(59, 130, 246, 0.3)'
              }
            }
          }}
        />
        
        <Tooltip title={isRecording ? "Stop recording" : "Voice input"}>
          <IconButton 
            color={isRecording ? "error" : "primary"}
            sx={{ ml: 1 }}
            onClick={toggleVoiceRecording}
          >
            {isRecording ? <CircularProgress size={24} color="error" /> : <MicIcon />}
          </IconButton>
        </Tooltip>
        
        <IconButton 
          type="submit" 
          color="primary" 
          sx={{ ml: 1 }}
          disabled={!input.trim() || isProcessing}
        >
          {isProcessing ? <CircularProgress size={24} /> : <SendIcon />}
        </IconButton>
      </Box>
    </Box>
  );
};

export default ChatInput;