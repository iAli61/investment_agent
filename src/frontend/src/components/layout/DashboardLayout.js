import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { 
  Box, 
  AppBar, 
  Toolbar, 
  Typography, 
  Button,
  IconButton,
  Drawer,
  useTheme,
  useMediaQuery
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import SettingsIcon from '@mui/icons-material/Settings';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import NavigationHeader from './NavigationHeader';
import ChatSidebar from '../chat/ChatSidebar';

// Width of the chat sidebar based on UI.png (27% of the screen)
const SIDEBAR_WIDTH = '27%';

const DashboardLayout = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <Box sx={{ display: 'flex', width: '100%' }}>
      <NavigationHeader 
        isMobile={isMobile}
        onMenuClick={handleDrawerToggle}
      />
      
      {/* Chat Sidebar - Persistent on desktop, drawer on mobile */}
      {isMobile ? (
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: '80%',
              bgcolor: 'background.paper',
            },
          }}
        >
          <ChatSidebar />
        </Drawer>
      ) : (
        <Box
          component="aside"
          sx={{
            width: SIDEBAR_WIDTH,
            flexShrink: 0,
            borderRight: 1,
            borderColor: 'divider',
          }}
        >
          <ChatSidebar />
        </Box>
      )}

      {/* Main Content Area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: isMobile ? '100%' : `calc(100% - ${SIDEBAR_WIDTH})`,
          p: 2,
          overflow: 'auto'
        }}
      >
        <Toolbar /> {/* Spacer for fixed AppBar */}
        <Outlet /> {/* Renders the current route */}
      </Box>
    </Box>
  );
};

export default DashboardLayout;