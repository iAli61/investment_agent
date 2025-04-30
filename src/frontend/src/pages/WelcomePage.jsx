import React from 'react';
import { Container, Box, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const WelcomePage = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="md" sx={{ py: 4, textAlign: 'center' }}>
      <Typography variant="h3" fontWeight="bold" gutterBottom>
        Welcome to Conversational Analysis Hub
      </Typography>
      <Typography variant="h6" color="text.secondary" gutterBottom>
        Your AI assistant to guide you through property investment analysis.
      </Typography>
      <Box sx={{ mt: 4, display: 'flex', gap: 2, justifyContent: 'center' }}>
        <Button
          variant="contained"
          color="primary"
          size="large"
          onClick={() => navigate('/app/new-analysis')}
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
    </Container>
  );
};

export default WelcomePage;
