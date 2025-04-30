import React from 'react';
import { 
  Box, 
  Grid, 
  Paper, 
  Typography,
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import HomeWorkIcon from '@mui/icons-material/HomeWork';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import TimelineIcon from '@mui/icons-material/Timeline';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';

const MetricCard = ({ metric }) => {
  const { id, name, value, trend, status } = metric;

  // Configure icon based on metric id
  const renderIcon = () => {
    switch (id) {
      case 'cap_rate':
        return <HomeWorkIcon sx={{ color: 'primary.main' }} />;
      case 'cash_on_cash':
        return <AccountBalanceIcon sx={{ color: 'primary.main' }} />;
      case 'roi':
        return <TimelineIcon sx={{ color: 'primary.main' }} />;
      case 'affordability':
        return <VerifiedUserIcon sx={{ color: 'primary.main' }} />;
      default:
        return <HomeWorkIcon sx={{ color: 'primary.main' }} />;
    }
  };

  // Configure color and text based on status
  const statusConfig = {
    good: {
      color: 'success.main',
      textColor: 'success.light',
      bgColor: 'rgba(16, 185, 129, 0.1)',
      borderColor: 'rgba(16, 185, 129, 0.2)',
    },
    warning: {
      color: 'warning.main',
      textColor: 'warning.light',
      bgColor: 'rgba(245, 158, 11, 0.1)',
      borderColor: 'rgba(245, 158, 11, 0.2)',
    },
    poor: {
      color: 'error.main',
      textColor: 'error.light',
      bgColor: 'rgba(239, 68, 68, 0.1)',
      borderColor: 'rgba(239, 68, 68, 0.2)',
    },
  };

  const config = statusConfig[status] || statusConfig.good;

  return (
    <Paper
      elevation={0}
      sx={{
        p: 2,
        borderRadius: 2,
        backgroundColor: config.bgColor,
        border: `1px solid ${config.borderColor}`,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {renderIcon()}
          <Typography variant="subtitle2" color="text.secondary" sx={{ ml: 1 }}>
            {name}
          </Typography>
        </Box>
        
        {trend !== null && (
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center',
              color: trend >= 0 ? 'success.main' : 'error.main',
              bgcolor: trend >= 0 ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
              px: 1,
              py: 0.5,
              borderRadius: 1,
            }}
          >
            {trend >= 0 ? (
              <TrendingUpIcon fontSize="small" sx={{ mr: 0.5 }} />
            ) : (
              <TrendingDownIcon fontSize="small" sx={{ mr: 0.5 }} />
            )}
            <Typography variant="caption" fontWeight="medium">
              {trend >= 0 ? '+' : ''}{trend}%
            </Typography>
          </Box>
        )}
      </Box>
      
      <Typography variant="h4" fontWeight="bold" sx={{ mt: 'auto' }}>
        {value}
      </Typography>
      
      {status === 'good' && (
        <Typography variant="caption" color={config.textColor} sx={{ mt: 1 }}>
          Good
        </Typography>
      )}
      
      {status === 'warning' && (
        <Typography variant="caption" color={config.textColor} sx={{ mt: 1 }}>
          Below Target
        </Typography>
      )}
    </Paper>
  );
};

const MetricsGrid = ({ metrics }) => {
  return (
    <Grid container spacing={3}>
      {metrics.map((metric) => (
        <Grid item xs={12} sm={6} md={3} key={metric.id}>
          <MetricCard metric={metric} />
        </Grid>
      ))}
    </Grid>
  );
};

export default MetricsGrid;