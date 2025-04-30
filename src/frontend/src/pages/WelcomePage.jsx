import React from 'react';
import { Box, Typography, Button, Paper } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import AnalyticsIcon from '@mui/icons-material/Analytics';

const WelcomePage = () => {
  const navigate = useNavigate();

  return (
    <Box sx={{ 
      width: '100%', 
      height: '100%',
      display: 'flex',
      flexDirection: 'column'
    }}>
      <Paper 
        elevation={0} 
        sx={{ 
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          p: { xs: 2, sm: 4 },
          m: { xs: 1, sm: 2 },
          borderRadius: 2,
          bgcolor: 'background.paper'
        }}
      >
        <Box 
          component="img"
          src="/assets/welcome-illustration.svg" 
          alt="Property Analysis Illustration"
          sx={{ 
            maxWidth: '400px', 
            width: '100%', 
            mb: 4,
            display: { xs: 'none', md: 'block' } 
          }}
          onError={(e) => {
            // Fallback if image fails to load
            e.target.style.display = 'none';
          }}
        />
        
        <Typography variant="h3" fontWeight="bold" textAlign="center" gutterBottom>
          Welcome to Conversational Analysis Hub
        </Typography>
        
        <Typography 
          variant="h6" 
          color="text.secondary" 
          textAlign="center" 
          gutterBottom
          sx={{ maxWidth: 600, mb: 4 }}
        >
          Your AI assistant to guide you through property investment analysis.
          Get market insights, affordability checks, and ROI calculations in one place.
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            color="primary"
            size="large"
            onClick={() => navigate('/app/new-analysis')}
            startIcon={<AnalyticsIcon />}
          >
            Start New Analysis
          </Button>
          <Button
            variant="outlined"
            color="inherit"
            size="large"
            onClick={() => navigate('/app/scenarios')}
          >
            View My Scenarios
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default WelcomePage;
