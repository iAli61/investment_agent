import React, { useState } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  Tabs, 
  Tab,
  Button,
  Divider,
  Chip
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import ShareIcon from '@mui/icons-material/Share';
import CompareArrowsIcon from '@mui/icons-material/CompareArrows';

// Import Components
import PropertyOverview from './PropertyOverview';
import AnalyticsSection from './AnalyticsSection';
import MetricsGrid from './MetricsGrid';
import DocumentUpload from './DocumentUpload';

/**
 * PropertyAnalysisDashboard - Main content area that displays property analysis
 * information based on the conversational context, as specified in UI design
 */
const PropertyAnalysisDashboard = ({ propertyData, analysisData, onSaveScenario }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [analysisStatus, setAnalysisStatus] = useState({
    isComplete: false,
    currentStep: 'market-analysis',
    progress: 65,
  });

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Paper
      elevation={0}
      sx={{
        height: '100%',
        p: 3,
        borderRadius: 2,
        bgcolor: 'background.paper',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        overflow: 'auto',
      }}
    >
      {/* Header with Analysis Status and Actions */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box>
          <Typography variant="h5" fontWeight="bold">
            Property Analysis
          </Typography>
          
          {!analysisStatus.isComplete && (
            <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
              <Chip 
                label={`${analysisStatus.currentStep
                  .split('-')
                  .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                  .join(' ')} in progress...`} 
                color="primary" 
                variant="outlined" 
                size="small"
              />
              <Typography variant="caption" sx={{ ml: 1, color: 'text.secondary' }}>
                {analysisStatus.progress}% complete
              </Typography>
            </Box>
          )}
        </Box>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button 
            startIcon={<SaveIcon />} 
            size="small" 
            variant="outlined"
            onClick={() => onSaveScenario && onSaveScenario()}
          >
            Save Scenario
          </Button>
          <Button 
            startIcon={<ShareIcon />} 
            size="small" 
            variant="outlined"
          >
            Share
          </Button>
          <Button 
            startIcon={<CompareArrowsIcon />} 
            size="small" 
            variant="text"
          >
            Compare
          </Button>
        </Box>
      </Box>
      
      {/* Property Overview Section */}
      <PropertyOverview propertyData={propertyData} />
      
      {/* Tabs Navigation */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs 
          value={activeTab} 
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          sx={{ 
            '& .MuiTab-root': { 
              textTransform: 'none',
              fontWeight: 500,
              minWidth: 120,
            },
          }}
        >
          <Tab label="Market Analysis" />
          <Tab label="Financials" />
          <Tab label="Cash Flow" />
          <Tab label="ROI Projections" />
          <Tab label="Risk Assessment" />
          <Tab label="Documents" />
        </Tabs>
      </Box>
      
      {/* Tab Content */}
      <Box sx={{ pt: 3, minHeight: '400px' }}>
        {/* Market Analysis Tab */}
        {activeTab === 0 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Market Analysis
            </Typography>
            <AnalyticsSection 
              marketAnalysisData={analysisData.marketData} 
              comparableProperties={analysisData.comparableProperties}
            />
          </Box>
        )}
        
        {/* Financials Tab */}
        {activeTab === 1 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Financial Breakdown
            </Typography>
            <MetricsGrid metrics={analysisData.financialMetrics} />
          </Box>
        )}
        
        {/* Cash Flow Tab */}
        {activeTab === 2 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Monthly Cash Flow Projections
            </Typography>
            <AnalyticsSection 
              cashFlowData={analysisData.cashFlowData} 
            />
          </Box>
        )}
        
        {/* ROI Projections Tab */}
        {activeTab === 3 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Return on Investment Projections
            </Typography>
            <AnalyticsSection 
              roiData={analysisData.roiData} 
            />
          </Box>
        )}
        
        {/* Risk Assessment Tab */}
        {activeTab === 4 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Risk Assessment
            </Typography>
            <MetricsGrid metrics={analysisData.riskMetrics} />
          </Box>
        )}
        
        {/* Documents Tab */}
        {activeTab === 5 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Property Documents
            </Typography>
            <DocumentUpload />
          </Box>
        )}
      </Box>
    </Paper>
  );
};

export default PropertyAnalysisDashboard;