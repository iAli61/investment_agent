import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Box,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import SettingsIcon from '@mui/icons-material/Settings';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';

const NavigationHeader = ({ isMobile, onMenuClick }) => {
  return (
    <AppBar 
      position="fixed" 
      sx={{ 
        zIndex: (theme) => theme.zIndex.drawer + 1,
        backgroundColor: 'background.paper',
        boxShadow: 'none',
        borderBottom: 1,
        borderColor: 'divider',
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        {/* Left side - Logo and Title */}
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {isMobile && (
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={onMenuClick}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}
          
          <Box component={RouterLink} to="/" sx={{ 
            display: 'flex', 
            alignItems: 'center',
            textDecoration: 'none',
            color: 'inherit'
          }}>
            <Box 
              component="img"
              src="/logo.svg"
              alt="Conversational Analysis Hub Logo"
              sx={{ height: 24, mr: 1 }}
            />
            <Typography 
              variant="h6" 
              noWrap 
              component="div"
              sx={{ display: { xs: 'none', sm: 'block' }, fontWeight: 'bold' }}
            >
              Conversational Analysis Hub
            </Typography>
          </Box>
        </Box>

        {/* Middle - Navigation Links */}
        <Box 
          sx={{ 
            display: { xs: 'none', md: 'flex' },
            gap: 2
          }}
        >
          <Button 
            component={RouterLink} 
            to="/app/scenarios" 
            color="inherit"
            sx={{ fontWeight: 500 }}
          >
            My Scenarios
          </Button>
          <Button 
            component={RouterLink} 
            to="/app/new-analysis" 
            color="inherit"
            sx={{ fontWeight: 500 }}
          >
            Start New Analysis
          </Button>
          <Button 
            component={RouterLink} 
            to="/app/knowledge-base" 
            color="inherit"
            sx={{ fontWeight: 500 }}
          >
            Knowledge Base
          </Button>
        </Box>

        {/* Right side - Settings and Profile */}
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton color="inherit" aria-label="settings">
            <SettingsIcon />
          </IconButton>
          <IconButton color="inherit" aria-label="profile">
            <AccountCircleIcon />
          </IconButton>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default NavigationHeader;