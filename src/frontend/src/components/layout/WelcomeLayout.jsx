import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Box, 
  Typography, 
  Button, 
  Paper, 
  Avatar, 
  TextField, 
  IconButton,
  Divider,
  useTheme,
  useMediaQuery,
  Drawer,
  AppBar,
  Toolbar,
  Menu,
  MenuItem,
  ListItem,
  ListItemIcon,
  ListItemText,
  List
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import HomeIcon from '@mui/icons-material/Home';
import ViewListIcon from '@mui/icons-material/ViewList';
import AddIcon from '@mui/icons-material/Add';
import SchoolIcon from '@mui/icons-material/School';
import ChatIcon from '@mui/icons-material/Chat';
import HelpIcon from '@mui/icons-material/Help';
import SettingsIcon from '@mui/icons-material/Settings';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import MenuIcon from '@mui/icons-material/Menu';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import WelcomePage from '../../pages/WelcomePage';

// Navigation items with icons and paths
const navItems = [
  { text: 'Dashboard', icon: <HomeIcon />, path: '/app' },
  { text: 'My Scenarios', icon: <ViewListIcon />, path: '/app/scenarios' },
  { text: 'New Analysis', icon: <AddIcon />, path: '/app/new-analysis' },
  { text: 'Knowledge Base', icon: <SchoolIcon />, path: '/app/knowledge-base' },
  { text: 'AI Assistant', icon: <ChatIcon />, path: '/app/chat' },
];

const WelcomeLayout = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isTablet = useMediaQuery(theme.breakpoints.down('lg'));
  
  // State for mobile drawer
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [chatSidebarOpen, setChatSidebarOpen] = useState(!isMobile);
  
  // State for user menu
  const [userMenuAnchor, setUserMenuAnchor] = useState(null);
  const [navMenuAnchor, setNavMenuAnchor] = useState(null);
  
  // State for chat messages (in a real app, this would likely be in a context)
  const [messages, setMessages] = useState([
    { id: 1, text: 'Welcome! How can I help you analyze a property today?', isUser: false },
    { id: 2, text: 'You can start by telling me an address or click "Start New Analysis" in the main panel.', isUser: false },
  ]);
  const [inputMessage, setInputMessage] = useState('');

  const handleSendMessage = () => {
    if (inputMessage.trim() === '') return;
    
    // Add user message
    setMessages([...messages, { id: Date.now(), text: inputMessage, isUser: true }]);
    
    // Clear input field
    setInputMessage('');
    
    // In a real app, we would send this message to the backend and get a response
    // Here we're just simulating a response after a delay
    setTimeout(() => {
      setMessages(prev => [...prev, { 
        id: Date.now(), 
        text: 'I understand you want to analyze a property. Would you like to start a new analysis?', 
        isUser: false 
      }]);
    }, 1000);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  const handleToggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };
  
  const handleToggleChatSidebar = () => {
    setChatSidebarOpen(!chatSidebarOpen);
  };
  
  const handleUserMenuOpen = (event) => {
    setUserMenuAnchor(event.currentTarget);
  };
  
  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };
  
  const handleNavMenuOpen = (event) => {
    setNavMenuAnchor(event.currentTarget);
  };
  
  const handleNavMenuClose = () => {
    setNavMenuAnchor(null);
  };
  
  const handleNavigation = (path) => {
    navigate(path);
    setNavMenuAnchor(null);
    setDrawerOpen(false);
  };

  // Chat sidebar component
  const ChatSidebar = () => (
    <Box 
      sx={{ 
        width: { xs: '100%', md: 320 },
        bgcolor: 'background.paper',
        borderRight: 1,
        borderColor: 'divider',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        position: { xs: 'fixed', md: 'relative' },
        zIndex: { xs: 1200, md: 'auto' },
        left: 0,
        top: 0,
      }}
    >
      {/* Top branding */}
      <Box sx={{ 
        p: 2, 
        borderBottom: 1, 
        borderColor: 'divider', 
        display: 'flex', 
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Avatar sx={{ bgcolor: 'primary.main', mr: 1 }}>
            <AnalyticsIcon />
          </Avatar>
          <Typography variant="h6" fontWeight="bold">Property Analyst</Typography>
        </Box>
        {isMobile && (
          <IconButton edge="end" onClick={handleToggleChatSidebar}>
            <MenuIcon />
          </IconButton>
        )}
      </Box>
      
      {/* Chat messages area */}
      <Box sx={{ flexGrow: 1, p: 2, overflowY: 'auto' }}>
        {messages.map((message) => (
          <Box key={message.id} sx={{ mb: 2 }}>
            <Paper 
              elevation={message.isUser ? 0 : 1}
              sx={{ 
                p: 2, 
                bgcolor: message.isUser ? 'primary.light' : 'background.default', 
                color: message.isUser ? 'primary.contrastText' : 'text.primary',
                borderRadius: 2,
                maxWidth: '85%',
                ml: message.isUser ? 'auto' : 0
              }}
            >
              <Typography variant="body1">
                {message.text}
              </Typography>
            </Paper>
          </Box>
        ))}
      </Box>
      
      {/* Chat input area */}
      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <TextField
            fullWidth
            placeholder="Type your message here..."
            size="small"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            sx={{ mr: 1 }}
            multiline
            maxRows={3}
          />
          <IconButton color="primary" onClick={handleSendMessage}>
            <SendIcon />
          </IconButton>
        </Box>
      </Box>
    </Box>
  );

  // Navigation drawer for mobile
  const NavigationDrawer = () => (
    <Drawer
      anchor="left"
      open={drawerOpen}
      onClose={() => setDrawerOpen(false)}
      sx={{
        '& .MuiDrawer-paper': {
          width: 250,
          bgcolor: 'background.paper',
        },
      }}
    >
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', alignItems: 'center' }}>
        <Avatar sx={{ bgcolor: 'primary.main', mr: 1 }}>
          <AnalyticsIcon />
        </Avatar>
        <Typography variant="h6" fontWeight="bold">Property Analyst</Typography>
      </Box>
      
      <List sx={{ width: '100%' }}>
        {navItems.map((item) => (
          <ListItem 
            button 
            key={item.text} 
            onClick={() => handleNavigation(item.path)}
            sx={{
              py: 1,
              borderRadius: 1,
              mx: 1,
              '&:hover': {
                bgcolor: 'action.hover',
              },
            }}
          >
            <ListItemIcon sx={{ minWidth: 40 }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
    </Drawer>
  );

  return (
    <Box 
      sx={{ 
        display: 'flex', 
        flexDirection: { xs: 'column', md: 'row' },
        height: '100vh',
        width: '100vw',
        overflow: 'hidden'
      }}
    >
      {/* Mobile navigation drawer */}
      <NavigationDrawer />
      
      {/* Chat Sidebar - conditionally rendered based on screen size and state */}
      {(chatSidebarOpen || !isMobile) && <ChatSidebar />}
      
      {/* Main Content Area */}
      <Box 
        sx={{ 
          flexGrow: 1, 
          display: 'flex', 
          flexDirection: 'column', 
          height: '100%',
          width: { xs: '100%', md: chatSidebarOpen ? 'calc(100% - 320px)' : '100%' },
          ml: { xs: 0, md: chatSidebarOpen ? '320px' : 0 },
          transition: theme => theme.transitions.create(['margin', 'width'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        {/* Top AppBar */}
        <AppBar 
          position="static" 
          color="default" 
          elevation={0}
          sx={{ 
            borderBottom: 1, 
            borderColor: 'divider',
            bgcolor: 'background.paper'
          }}
        >
          <Toolbar sx={{ justifyContent: 'space-between', px: { xs: 1, sm: 3 } }}>
            {/* Left section: Menu icon on mobile, title on desktop */}
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              {isMobile && (
                <IconButton 
                  edge="start"
                  color="inherit"
                  aria-label="menu"
                  onClick={handleToggleDrawer}
                  sx={{ mr: 1 }}
                >
                  <MenuIcon />
                </IconButton>
              )}
              
              {!isMobile && !chatSidebarOpen && (
                <IconButton 
                  edge="start"
                  color="inherit"
                  aria-label="chat"
                  onClick={handleToggleChatSidebar}
                  sx={{ mr: 1 }}
                >
                  <ChatIcon />
                </IconButton>
              )}
              
              <Typography variant="subtitle1" fontWeight="bold" noWrap>
                Conversational Analysis Hub
              </Typography>
            </Box>
            
            {/* Center section: Navigation buttons on desktop, menu on mobile */}
            <Box sx={{ display: { xs: 'none', lg: 'flex' } }}>
              {navItems.map((item) => (
                <Button 
                  key={item.text}
                  size="small" 
                  sx={{ mx: 0.5 }}
                  startIcon={item.icon}
                  onClick={() => navigate(item.path)}
                >
                  {item.text}
                </Button>
              ))}
            </Box>
            
            {/* Tablet navigation dropdown */}
            {isTablet && !isMobile && (
              <Box sx={{ display: 'flex' }}>
                <IconButton 
                  aria-label="navigation"
                  aria-controls="navigation-menu"
                  aria-haspopup="true"
                  onClick={handleNavMenuOpen}
                >
                  <MoreVertIcon />
                </IconButton>
                <Menu
                  id="navigation-menu"
                  anchorEl={navMenuAnchor}
                  keepMounted
                  open={Boolean(navMenuAnchor)}
                  onClose={handleNavMenuClose}
                >
                  {navItems.map((item) => (
                    <MenuItem key={item.text} onClick={() => handleNavigation(item.path)}>
                      <ListItemIcon>{item.icon}</ListItemIcon>
                      <Typography variant="body2">{item.text}</Typography>
                    </MenuItem>
                  ))}
                </Menu>
              </Box>
            )}
            
            {/* Right section: User controls */}
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              {!isMobile && (
                <>
                  <IconButton size="small" sx={{ ml: 0.5 }}>
                    <HelpIcon fontSize="small" />
                  </IconButton>
                  <IconButton size="small" sx={{ ml: 0.5 }}>
                    <SettingsIcon fontSize="small" />
                  </IconButton>
                </>
              )}
              <IconButton 
                size="small" 
                sx={{ ml: 0.5 }}
                onClick={handleUserMenuOpen}
              >
                <AccountCircleIcon fontSize="small" />
              </IconButton>
              
              <Menu
                id="user-menu"
                anchorEl={userMenuAnchor}
                keepMounted
                open={Boolean(userMenuAnchor)}
                onClose={handleUserMenuClose}
              >
                <MenuItem onClick={handleUserMenuClose}>Profile</MenuItem>
                <MenuItem onClick={handleUserMenuClose}>Settings</MenuItem>
                <MenuItem onClick={handleUserMenuClose}>Help</MenuItem>
                <Divider />
                <MenuItem onClick={handleUserMenuClose}>Logout</MenuItem>
              </Menu>
            </Box>
          </Toolbar>
        </AppBar>
        
        {/* Main Content - Welcome Page content */}
        <Box 
          sx={{ 
            display: 'grid',
            gridTemplateRows: 'auto 1fr auto',
            minHeight: 'calc(100vh - 64px)', // Subtracting AppBar height
            overflow: 'auto',
            bgcolor: 'background.default',
            width: '100%',
            p: { xs: 2, sm: 3 }
          }}
        >
          <WelcomePage />
        </Box>
        
        {/* Mobile chat toggle button */}
        {isMobile && !chatSidebarOpen && (
          <Box
            sx={{
              position: 'fixed',
              bottom: 16,
              right: 16,
              zIndex: 1000,
            }}
          >
            <IconButton
              color="primary"
              sx={{ 
                bgcolor: 'primary.main', 
                color: 'primary.contrastText',
                '&:hover': {
                  bgcolor: 'primary.dark',
                },
                width: 56,
                height: 56,
              }}
              onClick={handleToggleChatSidebar}
            >
              <ChatIcon />
            </IconButton>
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default WelcomeLayout;