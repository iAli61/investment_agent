import React, { useState } from 'react';
import { Container, Typography, Box, Paper, Button, Grid, TextField } from '@mui/material';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';

/**
 * NewAnalysis page - For starting a new property analysis
 */
const NewAnalysis = () => {
  const [address, setAddress] = useState('');
  
  const handleStartAnalysis = () => {
    // In a real implementation, this would trigger the analysis process
    console.log('Starting analysis for address:', address);
    alert(`Starting analysis for: ${address}`);
  };
  
  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Start New Analysis
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Begin by entering a property address to analyze investment potential.
        </Typography>
      </Box>
      
      <Paper 
        elevation={0} 
        sx={{ 
          p: 4, 
          borderRadius: 2,
          border: '1px solid',
          borderColor: 'divider',
          mb: 4 
        }}
      >
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Enter Property Address
            </Typography>
            <TextField
              fullWidth
              label="Property Address"
              placeholder="e.g., 123 Main St, Boston, MA 02108"
              variant="outlined"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              sx={{ mb: 2 }}
            />
            <Button 
              variant="contained" 
              size="large"
              endIcon={<ArrowForwardIcon />}
              onClick={handleStartAnalysis}
              disabled={!address.trim()}
            >
              Start Analysis
            </Button>
          </Grid>
        </Grid>
      </Paper>
      
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          How It Works
        </Typography>
        <Typography variant="body2" paragraph>
          Our AI-powered system will analyze the property and provide insights on:
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2, borderRadius: 2, height: '100%' }}>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                1. Market Analysis
              </Typography>
              <Typography variant="body2">
                Estimated market value, rent projections, and comparables from current market data.
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2, borderRadius: 2, height: '100%' }}>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                2. Financial Assessment
              </Typography>
              <Typography variant="body2">
                Affordability analysis, mortgage options, and personalized financial fit evaluation.
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2, borderRadius: 2, height: '100%' }}>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                3. ROI Calculation
              </Typography>
              <Typography variant="body2">
                Cash flow projections, cap rate, cash-on-cash return, and long-term value growth.
              </Typography>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default NewAnalysis;