import React from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Card, 
  CardMedia, 
  Divider,
  Paper,
} from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import RequestQuoteIcon from '@mui/icons-material/RequestQuote';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';

const PropertyOverview = ({ propertyData }) => {
  const { address, askingPrice, estimatedMarketValue, potentialMonthlyRent, image } = propertyData;

  return (
    <Box>
      <Typography variant="h5" fontWeight="bold" gutterBottom>
        {address}
      </Typography>
      
      <Grid container spacing={3} sx={{ mt: 1 }}>
        {/* Property Image */}
        <Grid item xs={12} md={4}>
          <Card sx={{ borderRadius: 2, overflow: 'hidden', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}>
            <CardMedia
              component="img"
              height="240"
              image={image}
              alt={`Property at ${address}`}
              sx={{ objectFit: 'cover' }}
            />
          </Card>
        </Grid>
        
        {/* Property Details */}
        <Grid item xs={12} md={8}>
          <Grid container spacing={2}>
            {/* Asking Price */}
            <Grid item xs={12} sm={4}>
              <Paper
                elevation={0}
                sx={{
                  p: 2,
                  height: '100%',
                  borderRadius: 2,
                  backgroundColor: 'rgba(59, 130, 246, 0.1)',
                  border: '1px solid rgba(59, 130, 246, 0.2)',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <RequestQuoteIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="subtitle2" color="text.secondary">
                    Asking Price
                  </Typography>
                </Box>
                <Typography variant="h5" fontWeight="bold">
                  {askingPrice}
                </Typography>
              </Paper>
            </Grid>
            
            {/* Estimated Market Value */}
            <Grid item xs={12} sm={4}>
              <Paper
                elevation={0}
                sx={{
                  p: 2,
                  height: '100%',
                  borderRadius: 2,
                  backgroundColor: 'rgba(16, 185, 129, 0.1)',
                  border: '1px solid rgba(16, 185, 129, 0.2)',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <ShowChartIcon color="secondary" sx={{ mr: 1 }} />
                  <Typography variant="subtitle2" color="text.secondary">
                    Estimated Market Value
                  </Typography>
                </Box>
                <Typography variant="h5" fontWeight="bold">
                  {estimatedMarketValue}
                </Typography>
              </Paper>
            </Grid>
            
            {/* Potential Monthly Rent */}
            <Grid item xs={12} sm={4}>
              <Paper
                elevation={0}
                sx={{
                  p: 2,
                  height: '100%',
                  borderRadius: 2,
                  backgroundColor: 'rgba(245, 158, 11, 0.1)',
                  border: '1px solid rgba(245, 158, 11, 0.2)',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <AttachMoneyIcon sx={{ mr: 1, color: 'warning.main' }} />
                  <Typography variant="subtitle2" color="text.secondary">
                    Potential Monthly Rent
                  </Typography>
                </Box>
                <Typography variant="h5" fontWeight="bold">
                  {potentialMonthlyRent}
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
      
      <Divider sx={{ my: 3 }} />
    </Box>
  );
};

export default PropertyOverview;