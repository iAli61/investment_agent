import React from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Paper,
} from '@mui/material';
import { 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';

const AnalyticsSection = ({ marketAnalysisData, cashFlowData }) => {
  return (
    <Grid container spacing={3}>
      {/* Market Analysis Chart */}
      <Grid item xs={12} md={6}>
        <Paper
          elevation={0}
          sx={{
            p: 2,
            borderRadius: 2,
            backgroundColor: 'background.paper',
            height: '100%',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <TrendingUpIcon color="primary" sx={{ mr: 1 }} />
            <Typography variant="h6">Market Analysis</Typography>
          </Box>
          
          <ResponsiveContainer width="100%" height={250}>
            <LineChart
              data={marketAnalysisData}
              margin={{
                top: 5,
                right: 30,
                left: 20,
                bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis 
                dataKey="month" 
                tick={{ fill: '#D1D5DB' }}
                axisLine={{ stroke: 'rgba(255,255,255,0.2)' }}
              />
              <YAxis 
                tick={{ fill: '#D1D5DB' }}
                axisLine={{ stroke: 'rgba(255,255,255,0.2)' }}
                width={45}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(31, 41, 55, 0.9)', 
                  border: 'none',
                  borderRadius: '8px',
                  color: '#F9FAFB',
                }}
              />
              <Line
                type="monotone"
                dataKey="value"
                name="Price/sqm ($)"
                stroke="#3B82F6"
                strokeWidth={2}
                dot={{ r: 4 }}
                activeDot={{ r: 6, fill: '#3B82F6', stroke: '#fff' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </Paper>
      </Grid>

      {/* Cash Flow Chart */}
      <Grid item xs={12} md={6}>
        <Paper
          elevation={0}
          sx={{
            p: 2,
            borderRadius: 2,
            backgroundColor: 'background.paper',
            height: '100%',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <AccountBalanceWalletIcon color="secondary" sx={{ mr: 1 }} />
            <Typography variant="h6">Cash Flow</Typography>
          </Box>
          
          <ResponsiveContainer width="100%" height={250}>
            <BarChart
              data={cashFlowData}
              margin={{
                top: 5,
                right: 30,
                left: 20,
                bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis 
                dataKey="month" 
                tick={{ fill: '#D1D5DB' }}
                axisLine={{ stroke: 'rgba(255,255,255,0.2)' }}
              />
              <YAxis 
                tick={{ fill: '#D1D5DB' }}
                axisLine={{ stroke: 'rgba(255,255,255,0.2)' }}
                width={45}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(31, 41, 55, 0.9)', 
                  border: 'none',
                  borderRadius: '8px',
                  color: '#F9FAFB',
                }}
              />
              <Legend 
                wrapperStyle={{ color: '#D1D5DB' }}
              />
              <Bar 
                dataKey="income" 
                name="Income" 
                fill="#10B981" 
                barSize={20}
              />
              <Bar 
                dataKey="expenses" 
                name="Expenses" 
                fill="#EF4444"
                barSize={20}
              />
            </BarChart>
          </ResponsiveContainer>
        </Paper>
      </Grid>
    </Grid>
  );
};

export default AnalyticsSection;