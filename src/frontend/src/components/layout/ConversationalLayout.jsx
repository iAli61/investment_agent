import React, { useState, useEffect } from 'react';
import { Outlet, NavLink, useLocation, useNavigate } from 'react-router-dom';
import { 
  Box, 
  Typography, 
  AppBar, 
  Toolbar, 
  IconButton, 
  Avatar,
  useTheme,
  useMediaQuery,
  Drawer,
  Button
} from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import MenuIcon from '@mui/icons-material/Menu';
import AddIcon from '@mui/icons-material/Add';
import SchoolIcon from '@mui/icons-material/School';

// Import Components
import ChatInterface from '../chat/ChatInterface';
import PropertyAnalysisDashboard from '../features/PropertyAnalysisDashboard';

// Sidebar width based on UI.png (27% of screen)
const SIDEBAR_WIDTH = '27%';
const SIDEBAR_WIDTH_PX = 380; // Fixed width for smaller screens

/**
 * ConversationalLayout component - Implements the UI design from UI.png with 
 * persistent chat sidebar and dynamic content area
 */
const ConversationalLayout = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('lg'));
  const navigate = useNavigate();
  const location = useLocation();

  // State for chat processing and dynamic main content
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeContent, setActiveContent] = useState('welcome');
  const [propertyData, setPropertyData] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);
  const [mobileOpen, setMobileOpen] = useState(false);

  // Mock property data
  const mockPropertyData = {
    address: '123 Main Street, Boston, MA 02108',
    askingPrice: '$450,000',
    estimatedMarketValue: '$465,000',
    potentialMonthlyRent: '$2,800',
    image: 'https://images.unsplash.com/photo-1568605114967-8130f3a36994?ixlib=rb-4.0.3&auto=format&fit=crop&w=1050&q=80',
  };

  // Mock analysis data
  const mockAnalysisData = {
    marketData: [
      { month: 'Jan', value: 4300 },
      { month: 'Feb', value: 4350 },
      { month: 'Mar', value: 4400 },
      { month: 'Apr', value: 4450 },
      { month: 'May', value: 4500 },
      { month: 'Jun', value: 4600 },
    ],
    cashFlowData: [
      { month: 'Jan', income: 2800, expenses: 1800 },
      { month: 'Feb', income: 2800, expenses: 1750 },
      { month: 'Mar', income: 2800, expenses: 1900 },
      { month: 'Apr', income: 2800, expenses: 1850 },
      { month: 'May', income: 2800, expenses: 1830 },
      { month: 'Jun', income: 2800, expenses: 1780 },
    ],
    roiData: [
      { year: '1', value: 5.7 },
      { year: '2', value: 6.2 },
      { year: '3', value: 6.5 },
      { year: '4', value: 6.9 },
      { year: '5', value: 7.2 },
    ],
    financialMetrics: [
      { id: 'cap_rate', name: 'Cap Rate', value: '5.2%', trend: -0.3, status: 'warning' },
      { id: 'cash_on_cash', name: 'Cash on Cash Return', value: '8.4%', trend: 1.2, status: 'good' },
      { id: 'roi', name: 'ROI', value: '12.7%', trend: -2.1, status: 'warning' },
      { id: 'affordability', name: 'Affordability Score', value: '85/100', trend: null, status: 'good' }
    ],
    riskMetrics: [
      { id: 'risk_score', name: 'Overall Risk', value: 'Moderate', trend: null, status: 'warning' },
      { id: 'market_volatility', name: 'Market Volatility', value: 'Low', trend: null, status: 'good' },
      { id: 'vacancy_risk', name: 'Vacancy Risk', value: 'Medium', trend: null, status: 'warning' },
      { id: 'liquidity_risk', name: 'Liquidity Risk', value: 'High', trend: null, status: 'bad' }
    ],
    comparableProperties: [
      { address: '125 Main St', price: '$455,000', sqft: 1850, bedBath: '3bd/2ba' },
      { address: '78 Oak Ave', price: '$468,000', sqft: 1920, bedBath: '3bd/2.5ba' },
      { address: '42 Elm St', price: '$442,000', sqft: 1780, bedBath: '3bd/2ba' },
    ]
  };

  // Handler for chat message sending
  const handleSendMessage = (message) => {
    console.log('Message sent:', message);
    setIsProcessing(true);
    
    // Simulate processing and response
    setTimeout(() => {
      setIsProcessing(false);
      
      // Show property analysis if message seems to contain an address
      if (message.toLowerCase().includes('main') || 
          message.toLowerCase().includes('street') || 
          message.toLowerCase().includes('analyze')) {
        setPropertyData(mockPropertyData);
        setAnalysisData(mockAnalysisData);
        setActiveContent('property-analysis');
      }
    }, 1500);
  };

  // Handlers for content changes requested by the chat
  const handleRequestPropertyInput = () => {
    setActiveContent('property-input');
  };

  const handleRequestFinancialInput = () => {
    setActiveContent('financial-input');
  };

  const handleViewScenarioComparison = () => {
    setActiveContent('scenario-comparison');
  };

  const handleSaveScenario = () => {
    console.log('Saving scenario...');
    // Would typically make an API call here
    
    // Show success message
    alert('Scenario saved successfully!');
  };

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  // Welcome content
  const renderWelcomeContent = () => (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      justifyContent: 'center',
      textAlign: 'center',
      height: '80%',
      p: 3 
    }}>
      <Box sx={{ mb: 4, p: 2, borderRadius: 2, bgcolor: 'background.paper' }}>
        <img 
          src="https://images.unsplash.com/photo-1560518883-ce09059eeffa?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80" 
          alt="Property Investment" 
          style={{ width: '100%', maxWidth: '400px', borderRadius: '8px' }}
        />
      </Box>
      <Typography variant="h4" gutterBottom fontWeight="bold">
        Welcome to Investment Property Analysis
      </Typography>
      <Typography variant="body1" sx={{ maxWidth: '600px', mb: 4 }}>
        Chat with our AI assistant to analyze investment properties, assess risk, and calculate ROI.
        Simply type a property address or ask a question to get started.
      </Typography>
      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', justifyContent: 'center' }}>
        <Button 
          variant="contained" 
          startIcon={<AddIcon />}
          onClick={() => handleRequestPropertyInput()}
        >
          Analyze New Property
        </Button>
        <Button 
          variant="outlined" 
          startIcon={<BookmarkIcon />} 
          onClick={() => navigate('/app/scenarios')}
        >
          View Saved Scenarios
        </Button>
        <Button 
          variant="outlined" 
          startIcon={<SchoolIcon />} 
          onClick={() => navigate('/app/knowledge-base')}
        >
          Investment Guides
        </Button>
      </Box>
    </Box>
  );

  // Dynamic content based on conversational context
  const renderDynamicContent = () => {
    switch (activeContent) {
      case 'property-analysis':
        return (
          <PropertyAnalysisDashboard 
            propertyData={propertyData}
            analysisData={analysisData}
            onSaveScenario={handleSaveScenario}
          />
        );
      case 'property-input':
        // In a real implementation, this would be a component for property details input
        return (
          <Box sx={{ p: 3, bgcolor: 'background.paper', borderRadius: 2 }}>
            <Typography variant="h5" gutterBottom fontWeight="bold">
              Property Details
            </Typography>
            <Typography variant="body1">
              Property input form would be displayed here.
            </Typography>
          </Box>
        );
      case 'financial-input':
        // In a real implementation, this would be a component for financial details input
        return (
          <Box sx={{ p: 3, bgcolor: 'background.paper', borderRadius: 2 }}>
            <Typography variant="h5" gutterBottom fontWeight="bold">
              Financial Details
            </Typography>
            <Typography variant="body1">
              Financial input form would be displayed here.
            </Typography>
          </Box>
        );
      case 'scenario-comparison':
        // In a real implementation, this would be a component for scenario comparison
        return (
          <Box sx={{ p: 3, bgcolor: 'background.paper', borderRadius: 2 }}>
            <Typography variant="h5" gutterBottom fontWeight="bold">
              Scenario Comparison
            </Typography>
            <Typography variant="body1">
              Scenario comparison view would be displayed here.
            </Typography>
          </Box>
        );
      case 'welcome':
      default:
        return renderWelcomeContent();
    }
  };
  
  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* Top Navigation */}
      <AppBar 
        position="fixed" 
        elevation={0}
        sx={{ 
          zIndex: (theme) => theme.zIndex.drawer + 1,
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <Toolbar>
          {isMobile && (
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}
          
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            Investment Analysis
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 3, alignItems: 'center' }}>
            <Button 
              color="inherit" 
              component={NavLink} 
              to="/app/scenarios"
              sx={{ 
                fontWeight: location.pathname === '/scenarios' ? 'bold' : 'normal',
                textTransform: 'none'
              }}
            >
              My Scenarios
            </Button>
            
            <Button 
              color="inherit" 
              component={NavLink} 
              to="/app/new-analysis"
              sx={{ 
                fontWeight: location.pathname === '/new-analysis' ? 'bold' : 'normal',
                textTransform: 'none'
              }}
            >
              Start New Analysis
            </Button>
            
            <Button 
              color="inherit" 
              component={NavLink} 
              to="/app/knowledge-base"
              sx={{ 
                fontWeight: location.pathname === '/knowledge-base' ? 'bold' : 'normal',
                textTransform: 'none'
              }}
            >
              Knowledge Base
            </Button>
            
            <IconButton color="inherit" size="small">
              <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>U</Avatar>
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>
      
      {/* Chat Sidebar - Drawer on mobile, fixed on desktop */}
      <Box
        component="nav"
        sx={{ 
          width: { lg: SIDEBAR_WIDTH }, 
          flexShrink: { lg: 0 }
        }}
      >
        {/* Mobile Drawer */}
        {isMobile ? (
          <Drawer
            variant="temporary"
            open={mobileOpen}
            onClose={handleDrawerToggle}
            ModalProps={{ keepMounted: true }}
            sx={{
              '& .MuiDrawer-paper': { 
                boxSizing: 'border-box', 
                width: SIDEBAR_WIDTH_PX,
                mt: '64px', // Toolbar height
                height: `calc(100% - 64px)`,
                borderRight: 1,
                borderColor: 'divider',
              },
            }}
          >
            <ChatInterface 
              onSendMessage={handleSendMessage}
              isProcessing={isProcessing}
              onRequestPropertyInput={handleRequestPropertyInput}
              onRequestFinancialInput={handleRequestFinancialInput}
              onViewScenarioComparison={handleViewScenarioComparison}
            />
          </Drawer>
        ) : (
          <Box
            sx={{ 
              width: SIDEBAR_WIDTH,
              position: 'fixed',
              top: '64px', // Toolbar height
              bottom: 0,
              left: 0,
              borderRight: 1,
              borderColor: 'divider',
              overflow: 'hidden',
            }}
          >
            <ChatInterface 
              onSendMessage={handleSendMessage}
              isProcessing={isProcessing}
              onRequestPropertyInput={handleRequestPropertyInput}
              onRequestFinancialInput={handleRequestFinancialInput}
              onViewScenarioComparison={handleViewScenarioComparison}
            />
          </Box>
        )}
      </Box>
      
      {/* Main Content Area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { lg: `calc(100% - ${SIDEBAR_WIDTH})` },
          ml: { lg: SIDEBAR_WIDTH },
          mt: '64px', // Toolbar height
          minHeight: 'calc(100vh - 64px)',
          bgcolor: 'background.default',
        }}
      >
        {/* Render content based on route or conversation context */}
        {location.pathname === '/' ? renderDynamicContent() : <Outlet />}
      </Box>
    </Box>
  );
};

export default ConversationalLayout;