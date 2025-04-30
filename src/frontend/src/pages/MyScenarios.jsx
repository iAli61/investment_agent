import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Container, 
  Tabs, 
  Tab, 
  Button,
  TextField,
  InputAdornment
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import AddIcon from '@mui/icons-material/Add';
import { useNavigate } from 'react-router-dom';

// Import components
import ScenarioComparison from '../components/features/ScenarioComparison';

/**
 * MyScenarios page - Displays saved property investment scenarios and allows comparison
 * as specified in the UI design document
 */
const MyScenarios = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  // Sample scenarios data for demonstration
  const scenarios = [
    {
      id: 1,
      name: 'Boston Main St',
      address: '123 Main Street, Boston, MA 02108',
      purchasePrice: '$450,000',
      monthlyRent: '$2,800',
      dateCreated: '2025-03-15',
      metrics: {
        capRate: 5.2,
        cashOnCash: 8.4,
        roi: 12.7,
        annualizedReturn: 7.8
      }
    },
    {
      id: 2,
      name: 'Cambridge Condo',
      address: '45 Harvard Square, Cambridge, MA 02138',
      purchasePrice: '$520,000',
      monthlyRent: '$3,200',
      dateCreated: '2025-04-02',
      metrics: {
        capRate: 5.8,
        cashOnCash: 7.9,
        roi: 14.2,
        annualizedReturn: 8.5
      }
    },
    {
      id: 3,
      name: 'Somerville Duplex',
      address: '78 Highland Ave, Somerville, MA 02143',
      purchasePrice: '$675,000',
      monthlyRent: '$4,100',
      dateCreated: '2025-04-18',
      metrics: {
        capRate: 6.1,
        cashOnCash: 9.2,
        roi: 15.3,
        annualizedReturn: 9.7
      }
    }
  ];

  // Filter scenarios based on search term
  const filteredScenarios = scenarios.filter(scenario => 
    scenario.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    scenario.address.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  // Handle scenario selection
  const handleSelectScenario = (scenarioId) => {
    if (scenarioId === 'new') {
      navigate('/new-analysis');
    } else {
      // In a real implementation, this would navigate to edit the specific scenario
      console.log(`Selected scenario: ${scenarioId}`);
    }
  };

  // Handle scenario deletion
  const handleDeleteScenario = (scenarioId) => {
    // In a real implementation, this would make an API call to delete the scenario
    console.log(`Deleting scenario: ${scenarioId}`);
    alert(`Scenario ${scenarioId} would be deleted in a real application.`);
  };

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Header */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        mb: 3 
      }}>
        <Typography variant="h4" fontWeight="bold">
          My Scenarios
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <TextField
            placeholder="Search scenarios..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            size="small"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            sx={{ minWidth: 240 }}
          />
          
          <Button 
            variant="contained" 
            startIcon={<AddIcon />}
            onClick={() => navigate('/new-analysis')}
          >
            New Scenario
          </Button>
        </Box>
      </Box>
      
      {/* Tabs Navigation */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs 
          value={activeTab} 
          onChange={handleTabChange}
          sx={{ 
            '& .MuiTab-root': { 
              textTransform: 'none',
              fontWeight: 500,
              minWidth: 100,
            },
          }}
        >
          <Tab label="Scenario Comparison" />
          <Tab label="All Scenarios" />
          <Tab label="Recently Created" />
          <Tab label="Highest ROI" />
        </Tabs>
      </Box>
      
      {/* Tab Content */}
      <Box sx={{ py: 3 }}>
        {/* Scenario Comparison Tab */}
        {activeTab === 0 && (
          <ScenarioComparison 
            scenarios={filteredScenarios}
            onSelectScenario={handleSelectScenario}
            onDeleteScenario={handleDeleteScenario}
          />
        )}
        
        {/* All Scenarios Tab */}
        {activeTab === 1 && (
          <Typography variant="body1">
            All scenarios would be displayed here in a list or grid format.
          </Typography>
        )}
        
        {/* Recently Created Tab */}
        {activeTab === 2 && (
          <Typography variant="body1">
            Recently created scenarios would be displayed here, sorted by creation date.
          </Typography>
        )}
        
        {/* Highest ROI Tab */}
        {activeTab === 3 && (
          <Typography variant="body1">
            Scenarios sorted by ROI would be displayed here.
          </Typography>
        )}
      </Box>
    </Container>
  );
};

export default MyScenarios;