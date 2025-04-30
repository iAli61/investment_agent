import React, { useState } from 'react';
import { 
  Fab, 
  Dialog, 
  DialogContent, 
  DialogTitle, 
  IconButton,
  useMediaQuery,
  useTheme
} from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import CloseIcon from '@mui/icons-material/Close';
import ChatInterface from '../chat/ChatInterface';

/**
 * Floating chat button that opens a dialog with the chat interface
 */
const FloatingChatButton = () => {
  const [open, setOpen] = useState(false);
  const theme = useTheme();
  const fullScreen = useMediaQuery(theme.breakpoints.down('md'));

  const handleOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  return (
    <>
      {/* Floating Action Button */}
      <Fab
        color="primary"
        aria-label="chat"
        onClick={handleOpen}
        sx={{
          position: 'fixed',
          bottom: 20,
          right: 20,
          zIndex: 999
        }}
      >
        <ChatIcon />
      </Fab>

      {/* Chat Dialog */}
      <Dialog
        open={open}
        onClose={handleClose}
        fullScreen={fullScreen}
        maxWidth="md"
        fullWidth
        sx={{
          '& .MuiDialog-paper': {
            height: fullScreen ? '100%' : '80vh',
            backgroundColor: theme.palette.background.default
          }
        }}
      >
        <DialogTitle sx={{ m: 0, p: 2, bgcolor: 'background.paper' }}>
          AI Investment Assistant
          <IconButton
            aria-label="close"
            onClick={handleClose}
            sx={{
              position: 'absolute',
              right: 8,
              top: 8,
              color: 'text.secondary'
            }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent sx={{ p: 0, display: 'flex', flexDirection: 'column' }}>
          <ChatInterface useStreaming={true} />
        </DialogContent>
      </Dialog>
    </>
  );
};

export default FloatingChatButton;