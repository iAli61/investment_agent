import React, { useState } from 'react';
import { 
  Box, 
  Container, 
  Grid, 
  Typography,
  Paper,
} from '@mui/material';
import PropertyOverview from '../components/features/PropertyOverview';
import AnalyticsSection from '../components/features/AnalyticsSection';
import MetricsGrid from '../components/features/MetricsGrid';
import DocumentUpload from '../components/features/DocumentUpload';

const HomePage = () => {
  // Mock property data for initial display
  const propertyData = {
    address: '123 Main Street, Boston, MA 02108',
    askingPrice: '$450,000',
    estimatedMarketValue: '$465,000',
    potentialMonthlyRent: '$2,800',
    image: 'https://images.unsplash.com/photo-1568605114967-8130f3a36994?ixlib=rb-4.0.3&auto=format&fit=crop&w=1050&q=80',
  };

  // Mock market analysis data
  const marketAnalysisData = [
    { month: 'Jan', value: 4300 },
    { month: 'Feb', value: 4350 },
    { month: 'Mar', value: 4400 },
    { month: 'Apr', value: 4450 },
    { month: 'May', value: 4500 },
    { month: 'Jun', value: 4600 },
  ];

  // Mock cash flow data
  const cashFlowData = [
    { month: 'Jan', income: 2800, expenses: 1800 },
    { month: 'Feb', value: 2800, expenses: 1750 },
    { month: 'Mar', value: 2800, expenses: 1900 },
    { month: 'Apr', value: 2800, expenses: 1850 },
    { month: 'May', value: 2800, expenses: 1830 },
    { month: 'Jun', value: 2800, expenses: 1780 },
  ];

  // Mock investment metrics
  const metrics = [
    { 
      id: 'cap_rate',
      name: 'Cap Rate', 
      value: '5.2%', 
      trend: -0.3,
      status: 'warning' 
    },
    { 
      id: 'cash_on_cash',
      name: 'Cash on Cash Return', 
      value: '8.4%', 
      trend: 1.2,
      status: 'good' 
    },
    { 
      id: 'roi',
      name: 'ROI', 
      value: '12.7%', 
      trend: -2.1,
      status: 'warning' 
    },
    { 
      id: 'affordability',
      name: 'Affordability Score', 
      value: '85/100', 
      trend: null,
      status: 'good' 
    }
  ];

  return (
    <Container maxWidth="xl" sx={{ py: 2 }}>
      <Box sx={{ mb: 4, mt: 2 }}>
        <Paper
          elevation={0}
          sx={{
            p: 3,
            borderRadius: 2,
            backgroundImage: 'linear-gradient(to right bottom, rgba(31, 41, 55, 0.8), rgba(17, 24, 39, 0.9))',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
          }}
        >
          {/* Property Overview Section */}
          <PropertyOverview propertyData={propertyData} />
          
          {/* Analytics Charts Section */}
          <AnalyticsSection 
            marketAnalysisData={marketAnalysisData} 
            cashFlowData={cashFlowData} 
          />
          
          {/* Metrics Grid Section */}
          <Box sx={{ my: 4 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Investment Performance Metrics
            </Typography>
            <MetricsGrid metrics={metrics} />
          </Box>
          
          {/* Document Upload Section */}
          <Box sx={{ mt: 4 }}>
            <DocumentUpload />
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default HomePage;