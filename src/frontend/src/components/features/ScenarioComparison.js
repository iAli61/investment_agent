import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  Card,
  CardContent,
  Grid,
  Button,
  Chip,
  IconButton,
  Divider
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import AddIcon from '@mui/icons-material/Add';
import ArrowRightAltIcon from '@mui/icons-material/ArrowRightAlt';
import InfoIcon from '@mui/icons-material/Info';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';

/**
 * ScenarioComparison component - Allows comparing different investment scenarios
 * as specified in the UI design document
 */
const ScenarioComparison = ({ scenarios = [], onSelectScenario, onDeleteScenario }) => {
  const [selectedScenarios, setSelectedScenarios] = useState([]);
  const [viewMode, setViewMode] = useState('table'); // 'table' or 'chart'

  // Helper to format percentage values
  const formatPercent = (value) => {
    return typeof value === 'number' ? `${value.toFixed(1)}%` : value;
  };
  
  // Helper to calculate difference between scenarios
  const calculateDifference = (metric, scenario1, scenario2) => {
    if (!scenario1 || !scenario2) return null;
    
    const val1 = parseFloat(scenario1.metrics[metric]?.toString().replace('%', ''));
    const val2 = parseFloat(scenario2.metrics[metric]?.toString().replace('%', ''));
    
    if (isNaN(val1) || isNaN(val2)) return null;
    
    return (val2 - val1).toFixed(1);
  };
  
  // Handler for selecting scenarios to compare
  const handleScenarioSelect = (scenarioId) => {
    if (selectedScenarios.includes(scenarioId)) {
      setSelectedScenarios(selectedScenarios.filter(id => id !== scenarioId));
    } else {
      // Limit to 2 scenarios for comparison
      if (selectedScenarios.length < 2) {
        setSelectedScenarios([...selectedScenarios, scenarioId]);
      } else {
        // Replace the first selected scenario
        setSelectedScenarios([selectedScenarios[1], scenarioId]);
      }
    }
  };
  
  // Get the selected scenario objects
  const getSelectedScenarioObjects = () => {
    return scenarios.filter(scenario => selectedScenarios.includes(scenario.id));
  };
  
  // Prepare data for chart visualization
  const prepareChartData = () => {
    const selected = getSelectedScenarioObjects();
    if (selected.length === 0) return [];
    
    const metrics = ['capRate', 'cashOnCash', 'roi', 'annualizedReturn'];
    const chartData = metrics.map(metric => {
      const data = { name: metric.replace(/([A-Z])/g, ' $1').trim() };
      
      selected.forEach((scenario, index) => {
        const value = parseFloat(scenario.metrics[metric]?.toString().replace('%', '')) || 0;
        data[`Scenario ${index + 1}`] = value;
      });
      
      return data;
    });
    
    return chartData;
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" fontWeight="bold" gutterBottom>
          Scenario Comparison
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Compare different investment scenarios side by side to make better investment decisions.
        </Typography>
      </Box>
      
      {/* Scenario Selection Cards */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
          Your Saved Scenarios
        </Typography>
        <Grid container spacing={2}>
          {scenarios.map(scenario => (
            <Grid item xs={12} sm={6} md={4} key={scenario.id}>
              <Card 
                sx={{ 
                  borderRadius: 2,
                  border: selectedScenarios.includes(scenario.id) 
                    ? '2px solid' 
                    : '1px solid',
                  borderColor: selectedScenarios.includes(scenario.id) 
                    ? 'primary.main' 
                    : 'divider',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  '&:hover': {
                    boxShadow: 3,
                    borderColor: 'primary.main',
                  },
                }}
                onClick={() => handleScenarioSelect(scenario.id)}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 1 }}>
                      {scenario.name}
                    </Typography>
                    
                    {selectedScenarios.includes(scenario.id) && (
                      <Chip 
                        label={`Scenario ${selectedScenarios.indexOf(scenario.id) + 1}`} 
                        color="primary" 
                        size="small" 
                      />
                    )}
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {scenario.address}
                  </Typography>
                  
                  <Divider sx={{ my: 1.5 }} />
                  
                  <Grid container spacing={1}>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Purchase Price
                      </Typography>
                      <Typography variant="subtitle2">
                        {scenario.purchasePrice}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Monthly Rent
                      </Typography>
                      <Typography variant="subtitle2">
                        {scenario.monthlyRent}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Cap Rate
                      </Typography>
                      <Typography variant="subtitle2">
                        {formatPercent(scenario.metrics.capRate)}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Cash on Cash
                      </Typography>
                      <Typography variant="subtitle2">
                        {formatPercent(scenario.metrics.cashOnCash)}
                      </Typography>
                    </Grid>
                  </Grid>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                    <IconButton size="small" onClick={(e) => {
                      e.stopPropagation();
                      onSelectScenario && onSelectScenario(scenario.id);
                    }}>
                      <EditIcon fontSize="small" />
                    </IconButton>
                    <IconButton size="small" color="error" onClick={(e) => {
                      e.stopPropagation();
                      onDeleteScenario && onDeleteScenario(scenario.id);
                    }}>
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
          
          {/* Add New Scenario Card */}
          <Grid item xs={12} sm={6} md={4}>
            <Card 
              sx={{ 
                borderRadius: 2,
                border: '1px dashed',
                borderColor: 'divider',
                bgcolor: 'background.default',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                minHeight: '240px',
                cursor: 'pointer',
                '&:hover': {
                  borderColor: 'primary.main',
                },
              }}
              onClick={() => onSelectScenario && onSelectScenario('new')}
            >
              <CardContent sx={{ textAlign: 'center' }}>
                <AddIcon sx={{ fontSize: 40, color: 'text.secondary', mb: 1 }} />
                <Typography color="text.secondary">
                  Add New Scenario
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
      
      {/* Comparison Section */}
      {selectedScenarios.length > 0 && (
        <Paper 
          elevation={0} 
          sx={{ 
            p: 3, 
            borderRadius: 2,
            border: '1px solid',
            borderColor: 'divider',
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6" fontWeight="bold">
              Comparison Details
            </Typography>
            
            <Box>
              <Button 
                variant={viewMode === 'table' ? 'contained' : 'outlined'}
                size="small"
                onClick={() => setViewMode('table')}
                sx={{ mr: 1 }}
              >
                Table View
              </Button>
              <Button 
                variant={viewMode === 'chart' ? 'contained' : 'outlined'}
                size="small"
                onClick={() => setViewMode('chart')}
              >
                Chart View
              </Button>
            </Box>
          </Box>
          
          {viewMode === 'table' ? (
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 'bold' }}>Metrics</TableCell>
                    {getSelectedScenarioObjects().map((scenario, index) => (
                      <TableCell key={scenario.id} sx={{ fontWeight: 'bold' }}>
                        Scenario {index + 1}: {scenario.name}
                      </TableCell>
                    ))}
                    {selectedScenarios.length === 2 && (
                      <TableCell sx={{ fontWeight: 'bold' }}>Difference</TableCell>
                    )}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {/* Property Details */}
                  <TableRow>
                    <TableCell component="th" scope="row" sx={{ fontWeight: 'bold', bgcolor: 'background.default' }}>
                      Property Details
                    </TableCell>
                    {getSelectedScenarioObjects().map((scenario) => (
                      <TableCell key={`${scenario.id}-details`} sx={{ bgcolor: 'background.default' }}></TableCell>
                    ))}
                    {selectedScenarios.length === 2 && (
                      <TableCell sx={{ bgcolor: 'background.default' }}></TableCell>
                    )}
                  </TableRow>
                  <TableRow>
                    <TableCell>Purchase Price</TableCell>
                    {getSelectedScenarioObjects().map((scenario) => (
                      <TableCell key={`${scenario.id}-price`}>{scenario.purchasePrice}</TableCell>
                    ))}
                    {selectedScenarios.length === 2 && (
                      <TableCell>
                        {calculateDifference('purchasePrice', 
                          getSelectedScenarioObjects()[0], 
                          getSelectedScenarioObjects()[1])}
                      </TableCell>
                    )}
                  </TableRow>
                  <TableRow>
                    <TableCell>Monthly Rent</TableCell>
                    {getSelectedScenarioObjects().map((scenario) => (
                      <TableCell key={`${scenario.id}-rent`}>{scenario.monthlyRent}</TableCell>
                    ))}
                    {selectedScenarios.length === 2 && (
                      <TableCell>
                        {calculateDifference('monthlyRent', 
                          getSelectedScenarioObjects()[0], 
                          getSelectedScenarioObjects()[1])}
                      </TableCell>
                    )}
                  </TableRow>
                  
                  {/* Investment Metrics */}
                  <TableRow>
                    <TableCell component="th" scope="row" sx={{ fontWeight: 'bold', bgcolor: 'background.default' }}>
                      Investment Metrics
                    </TableCell>
                    {getSelectedScenarioObjects().map((scenario) => (
                      <TableCell key={`${scenario.id}-metrics-header`} sx={{ bgcolor: 'background.default' }}></TableCell>
                    ))}
                    {selectedScenarios.length === 2 && (
                      <TableCell sx={{ bgcolor: 'background.default' }}></TableCell>
                    )}
                  </TableRow>
                  <TableRow>
                    <TableCell>Cap Rate</TableCell>
                    {getSelectedScenarioObjects().map((scenario) => (
                      <TableCell key={`${scenario.id}-cap-rate`}>
                        {formatPercent(scenario.metrics.capRate)}
                      </TableCell>
                    ))}
                    {selectedScenarios.length === 2 && (
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {calculateDifference('capRate', 
                            getSelectedScenarioObjects()[0], 
                            getSelectedScenarioObjects()[1])}%
                          <ArrowRightAltIcon 
                            color={parseFloat(calculateDifference('capRate', 
                              getSelectedScenarioObjects()[0], 
                              getSelectedScenarioObjects()[1])) > 0 ? 'success' : 'error'} 
                          />
                        </Box>
                      </TableCell>
                    )}
                  </TableRow>
                  <TableRow>
                    <TableCell>Cash on Cash Return</TableCell>
                    {getSelectedScenarioObjects().map((scenario) => (
                      <TableCell key={`${scenario.id}-coc`}>
                        {formatPercent(scenario.metrics.cashOnCash)}
                      </TableCell>
                    ))}
                    {selectedScenarios.length === 2 && (
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {calculateDifference('cashOnCash', 
                            getSelectedScenarioObjects()[0], 
                            getSelectedScenarioObjects()[1])}%
                          <ArrowRightAltIcon 
                            color={parseFloat(calculateDifference('cashOnCash', 
                              getSelectedScenarioObjects()[0], 
                              getSelectedScenarioObjects()[1])) > 0 ? 'success' : 'error'} 
                          />
                        </Box>
                      </TableCell>
                    )}
                  </TableRow>
                  <TableRow>
                    <TableCell>Return on Investment</TableCell>
                    {getSelectedScenarioObjects().map((scenario) => (
                      <TableCell key={`${scenario.id}-roi`}>
                        {formatPercent(scenario.metrics.roi)}
                      </TableCell>
                    ))}
                    {selectedScenarios.length === 2 && (
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {calculateDifference('roi', 
                            getSelectedScenarioObjects()[0], 
                            getSelectedScenarioObjects()[1])}%
                          <ArrowRightAltIcon 
                            color={parseFloat(calculateDifference('roi', 
                              getSelectedScenarioObjects()[0], 
                              getSelectedScenarioObjects()[1])) > 0 ? 'success' : 'error'} 
                          />
                        </Box>
                      </TableCell>
                    )}
                  </TableRow>
                  <TableRow>
                    <TableCell>Annualized Return (5yr)</TableCell>
                    {getSelectedScenarioObjects().map((scenario) => (
                      <TableCell key={`${scenario.id}-annualized`}>
                        {formatPercent(scenario.metrics.annualizedReturn)}
                      </TableCell>
                    ))}
                    {selectedScenarios.length === 2 && (
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {calculateDifference('annualizedReturn', 
                            getSelectedScenarioObjects()[0], 
                            getSelectedScenarioObjects()[1])}%
                          <ArrowRightAltIcon 
                            color={parseFloat(calculateDifference('annualizedReturn', 
                              getSelectedScenarioObjects()[0], 
                              getSelectedScenarioObjects()[1])) > 0 ? 'success' : 'error'} 
                          />
                        </Box>
                      </TableCell>
                    )}
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Box sx={{ height: 400 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={prepareChartData()}
                  margin={{
                    top: 20,
                    right: 30,
                    left: 20,
                    bottom: 5,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis label={{ value: 'Percentage', angle: -90, position: 'insideLeft' }} />
                  <Tooltip formatter={(value) => [`${value}%`, '']} />
                  <Legend />
                  {getSelectedScenarioObjects().map((scenario, index) => (
                    <Bar 
                      key={scenario.id} 
                      dataKey={`Scenario ${index + 1}`} 
                      fill={index === 0 ? '#3B82F6' : '#10B981'} 
                    />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </Box>
          )}
          
          <Box sx={{ mt: 3, display: 'flex', alignItems: 'center' }}>
            <InfoIcon fontSize="small" sx={{ color: 'text.secondary', mr: 1 }} />
            <Typography variant="body2" color="text.secondary">
              Select up to 2 scenarios to compare their investment metrics side by side.
            </Typography>
          </Box>
        </Paper>
      )}
    </Box>
  );
};

// Sample scenario data for demonstration
ScenarioComparison.defaultProps = {
  scenarios: [
    {
      id: 1,
      name: 'Boston Main St',
      address: '123 Main Street, Boston, MA 02108',
      purchasePrice: '$450,000',
      monthlyRent: '$2,800',
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
      metrics: {
        capRate: 6.1,
        cashOnCash: 9.2,
        roi: 15.3,
        annualizedReturn: 9.7
      }
    }
  ]
};

export default ScenarioComparison;