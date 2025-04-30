import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  Button, 
  CircularProgress,
  Alert,
  Grid,
  Divider,
  Chip,
  Tabs,
  Tab,
  Paper,
  LinearProgress
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import EditIcon from '@mui/icons-material/Edit';
import CalculateIcon from '@mui/icons-material/Calculate';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import apiService from '../../services/api';

/**
 * ScenarioDetail component for displaying detailed scenario information
 * and running analysis
 */
const ScenarioDetail = () => {
  const { propertyId, scenarioId } = useParams();
  const navigate = useNavigate();
  const [scenario, setScenario] = useState(null);
  const [property, setProperty] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [eventSource, setEventSource] = useState(null);
  const updateTimerRef = useRef(null);

  // Fetch scenario data when component mounts or scenarioId changes
  useEffect(() => {
    fetchScenarioData();
    
    // Set up SSE connection for updates
    setupUpdateListener();
    
    // Cleanup on unmount
    return () => {
      if (eventSource) {
        eventSource.close();
      }
      if (updateTimerRef.current) {
        clearInterval(updateTimerRef.current);
      }
    };
  }, [propertyId, scenarioId]);

  /**
   * Set up server-sent events listener for real-time updates
   */
  const setupUpdateListener = () => {
    try {
      // Generate a unique client ID
      const clientId = `scenario_${scenarioId}_${Date.now()}`;
      
      // Close any existing EventSource
      if (eventSource) {
        eventSource.close();
      }
      
      // Create new EventSource
      const newEventSource = apiService.subscribeToUpdates(clientId, {
        scenarioId: scenarioId,
        propertyId: propertyId
      });
      
      // Store the event source for cleanup
      setEventSource(newEventSource);
      
      // Listen for server-sent events
      newEventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Handle different event types
          switch (data.event_type) {
            case 'analysis_status':
              if (data.data.scenario_id === Number(scenarioId)) {
                setAnalyzing(data.data.status === 'analyzing');
              }
              break;
              
            case 'analysis_complete':
              if (data.data.scenario_id === Number(scenarioId)) {
                setAnalyzing(false);
                // Refresh the scenario data to get the latest results
                fetchScenarioData();
              }
              break;
              
            case 'analysis_error':
              if (data.data.scenario_id === Number(scenarioId)) {
                setAnalyzing(false);
                setError(`Analysis error: ${data.data.message}`);
              }
              break;
              
            default:
              break;
          }
        } catch (error) {
          console.error('Error parsing SSE data:', error);
        }
      };
      
      newEventSource.onerror = (error) => {
        console.error('SSE error:', error);
        
        // Attempt to reconnect in case of connection issues
        if (updateTimerRef.current) {
          clearInterval(updateTimerRef.current);
        }
        
        // Poll for updates as a fallback if SSE fails
        updateTimerRef.current = setInterval(() => {
          if (!analyzing) {
            fetchScenarioData();
          }
        }, 10000); // Poll every 10 seconds
      };
    } catch (error) {
      console.error('Error setting up SSE:', error);
    }
  };

  /**
   * Fetch scenario and property data
   */
  const fetchScenarioData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch scenario details
      const scenarioData = await apiService.getScenarioById(scenarioId);
      setScenario(scenarioData);
      
      // Check if the scenario is currently being analyzed
      if (scenarioData.status === 'analyzing') {
        setAnalyzing(true);
      } else {
        setAnalyzing(false);
      }
      
      // Fetch property details
      const propertyData = await apiService.getPropertyById(propertyId);
      setProperty(propertyData);
    } catch (err) {
      console.error('Error fetching scenario data:', err);
      setError('Failed to load scenario data. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle tab change
   * @param {Object} event - Tab change event
   * @param {number} newValue - New tab index
   */
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  /**
   * Navigate back to property detail page
   */
  const handleBackToProperty = () => {
    navigate(`/properties/${propertyId}`);
  };

  /**
   * Navigate to edit scenario page
   */
  const handleEditScenario = () => {
    navigate(`/properties/${propertyId}/scenarios/${scenarioId}/edit`);
  };

  /**
   * Run analysis on the scenario
   */
  const handleRunAnalysis = async () => {
    try {
      setAnalyzing(true);
      setError(null);
      
      // Run analysis on the scenario
      await apiService.analyzeScenario(scenarioId);
      
      // The actual results will be updated via SSE or polling
    } catch (err) {
      console.error('Error running analysis:', err);
      setError('Failed to run analysis. Please try again later.');
      setAnalyzing(false);
    }
  };

  /**
   * Format currency value
   * @param {number} value - Value to format
   * @returns {string} Formatted currency string
   */
  const formatCurrency = (value) => {
    if (value == null) return 'N/A';
    return new Intl.NumberFormat('en-US', { 
      style: 'currency', 
      currency: 'USD',
      maximumFractionDigits: 0 
    }).format(value);
  };

  /**
   * Format percentage value
   * @param {number} value - Value to format
   * @returns {string} Formatted percentage string
   */
  const formatPercentage = (value) => {
    if (value == null) return 'N/A';
    return new Intl.NumberFormat('en-US', { 
      style: 'percent',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2 
    }).format(value / 100);
  };

  // Overview tab content
  const renderOverview = () => {
    if (!scenario || !property) return null;
    
    const { results } = scenario;
    
    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Key Metrics
              </Typography>
              
              <Box sx={{ mt: 2 }}>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Cash on Cash Return</Typography>
                    <Typography variant="h6" fontWeight="bold">
                      {formatPercentage(results?.cash_on_cash_return)}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Cap Rate</Typography>
                    <Typography variant="h6" fontWeight="bold">
                      {formatPercentage(results?.cap_rate)}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Monthly Cash Flow</Typography>
                    <Typography 
                      variant="h6" 
                      fontWeight="bold"
                      color={
                        (results?.monthly_cash_flow || 0) > 0 
                          ? 'success.main' 
                          : (results?.monthly_cash_flow || 0) < 0 
                            ? 'error.main' 
                            : 'text.primary'
                      }
                    >
                      {formatCurrency(results?.monthly_cash_flow)}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Annual Cash Flow</Typography>
                    <Typography 
                      variant="h6" 
                      fontWeight="bold"
                      color={
                        (results?.annual_cash_flow || 0) > 0 
                          ? 'success.main' 
                          : (results?.annual_cash_flow || 0) < 0 
                            ? 'error.main' 
                            : 'text.primary'
                      }
                    >
                      {formatCurrency(results?.annual_cash_flow)}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Total Investment</Typography>
                    <Typography variant="body1" fontWeight="medium">
                      {formatCurrency(results?.total_investment)}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">IRR (5 year)</Typography>
                    <Typography variant="body1" fontWeight="medium">
                      {formatPercentage(results?.irr_5year)}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">ROI (5 year)</Typography>
                    <Typography variant="body1" fontWeight="medium">
                      {formatPercentage(results?.roi_5year)}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Break-even Point</Typography>
                    <Typography variant="body1" fontWeight="medium">
                      {results?.break_even_point 
                        ? `${results.break_even_point} months`
                        : 'N/A'}
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Financing Summary
              </Typography>
              
              <Box sx={{ mt: 2 }}>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Purchase Price</Typography>
                    <Typography variant="body1" fontWeight="medium">
                      {formatCurrency(property.property_details?.purchase_price)}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Down Payment</Typography>
                    <Typography variant="body1">
                      {formatCurrency(scenario.financing_params?.down_payment)}
                      {scenario.financing_params?.down_payment_percentage && 
                        ` (${scenario.financing_params.down_payment_percentage}%)`}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Loan Amount</Typography>
                    <Typography variant="body1">
                      {formatCurrency(scenario.financing_params?.loan_amount)}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Interest Rate</Typography>
                    <Typography variant="body1">
                      {scenario.financing_params?.interest_rate
                        ? `${scenario.financing_params.interest_rate}%`
                        : 'N/A'}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Loan Term</Typography>
                    <Typography variant="body1">
                      {scenario.financing_params?.loan_term
                        ? `${scenario.financing_params.loan_term} years`
                        : 'N/A'}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Monthly Payment</Typography>
                    <Typography variant="body1">
                      {formatCurrency(results?.monthly_mortgage_payment)}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Closing Costs</Typography>
                    <Typography variant="body1">
                      {formatCurrency(scenario.financing_params?.closing_costs)}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Upfront Repairs</Typography>
                    <Typography variant="body1">
                      {formatCurrency(scenario.financing_params?.repair_costs)}
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
            </Grid>
            
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                Income & Expenses
              </Typography>
              
              <Box sx={{ mt: 2 }}>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                      Income
                    </Typography>
                    
                    <Grid container spacing={1}>
                      <Grid item xs={8}>
                        <Typography variant="body2" color="text.secondary">Monthly Rental Income</Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="body1" align="right">
                          {formatCurrency(results?.monthly_rental_income)}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={8}>
                        <Typography variant="body2" color="text.secondary">Other Income</Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="body1" align="right">
                          {formatCurrency(scenario.rental_params?.other_income)}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={8}>
                        <Typography variant="body2" color="text.secondary">Vacancy Loss</Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="body1" align="right" color="error.main">
                          {formatCurrency(results?.vacancy_loss)}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={8}>
                        <Typography variant="body2" fontWeight="bold">Total Income</Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="body1" fontWeight="bold" align="right">
                          {formatCurrency(results?.effective_gross_income)}
                        </Typography>
                      </Grid>
                    </Grid>
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                      Expenses
                    </Typography>
                    
                    <Grid container spacing={1}>
                      <Grid item xs={8}>
                        <Typography variant="body2" color="text.secondary">Property Taxes</Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="body1" align="right">
                          {formatCurrency(scenario.expense_params?.property_tax)}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={8}>
                        <Typography variant="body2" color="text.secondary">Insurance</Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="body1" align="right">
                          {formatCurrency(scenario.expense_params?.insurance)}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={8}>
                        <Typography variant="body2" color="text.secondary">Maintenance</Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="body1" align="right">
                          {formatCurrency(scenario.expense_params?.maintenance)}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={8}>
                        <Typography variant="body2" color="text.secondary">Property Management</Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="body1" align="right">
                          {formatCurrency(scenario.expense_params?.property_management)}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={8}>
                        <Typography variant="body2" color="text.secondary">Utilities</Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="body1" align="right">
                          {formatCurrency(scenario.expense_params?.utilities)}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={8}>
                        <Typography variant="body2" fontWeight="bold">Total Expenses</Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="body1" fontWeight="bold" align="right">
                          {formatCurrency(results?.total_monthly_expenses)}
                        </Typography>
                      </Grid>
                    </Grid>
                  </Grid>
                </Grid>
              </Box>
            </Grid>
            
            {scenario.warnings && scenario.warnings.length > 0 && (
              <Grid item xs={12}>
                <Alert severity="warning" sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" fontWeight="bold">
                    Analysis Warnings
                  </Typography>
                  <ul>
                    {scenario.warnings.map((warning, index) => (
                      <li key={index}>{warning}</li>
                    ))}
                  </ul>
                </Alert>
              </Grid>
            )}
          </Grid>
        </CardContent>
      </Card>
    );
  };

  // Parameters tab content
  const renderParameters = () => {
    if (!scenario) return null;
    
    const { financing_params, rental_params, expense_params } = scenario;
    
    return (
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Financing Parameters
              </Typography>
              
              <Box component="ul" sx={{ pl: 2 }}>
                {Object.entries(financing_params || {}).map(([key, value]) => (
                  <Box component="li" key={key} sx={{ mb: 1 }}>
                    <Typography variant="body2" color="text.secondary" component="span" sx={{ textTransform: 'capitalize' }}>
                      {key.replace(/_/g, ' ')}:
                    </Typography>{' '}
                    <Typography variant="body1" component="span">
                      {typeof value === 'number' && (key.includes('rate') || key.includes('percentage')) 
                        ? `${value}%` 
                        : typeof value === 'number' && (key.includes('price') || key.includes('cost') || key.includes('amount') || key.includes('payment'))
                          ? formatCurrency(value)
                          : value}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Rental Parameters
              </Typography>
              
              <Box component="ul" sx={{ pl: 2 }}>
                {Object.entries(rental_params || {}).map(([key, value]) => (
                  <Box component="li" key={key} sx={{ mb: 1 }}>
                    <Typography variant="body2" color="text.secondary" component="span" sx={{ textTransform: 'capitalize' }}>
                      {key.replace(/_/g, ' ')}:
                    </Typography>{' '}
                    <Typography variant="body1" component="span">
                      {typeof value === 'number' && (key.includes('rate') || key.includes('percentage')) 
                        ? `${value}%` 
                        : typeof value === 'number' && (key.includes('rent') || key.includes('income'))
                          ? formatCurrency(value)
                          : value}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Expense Parameters
              </Typography>
              
              <Box component="ul" sx={{ pl: 2 }}>
                {Object.entries(expense_params || {}).map(([key, value]) => (
                  <Box component="li" key={key} sx={{ mb: 1 }}>
                    <Typography variant="body2" color="text.secondary" component="span" sx={{ textTransform: 'capitalize' }}>
                      {key.replace(/_/g, ' ')}:
                    </Typography>{' '}
                    <Typography variant="body1" component="span">
                      {typeof value === 'number' && (key.includes('rate') || key.includes('percentage')) 
                        ? `${value}%` 
                        : typeof value === 'number'
                          ? formatCurrency(value)
                          : value}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error && !scenario) {
    return (
      <Alert severity="error" sx={{ mt: 3 }}>
        {error}
      </Alert>
    );
  }

  if (!scenario) {
    return (
      <Alert severity="info" sx={{ mt: 3 }}>
        Scenario not found.
      </Alert>
    );
  }

  return (
    <Box sx={{ py: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <Button 
          startIcon={<ArrowBackIcon />} 
          onClick={handleBackToProperty}
          sx={{ mr: 2 }}
        >
          Back to Property
        </Button>
      </Box>
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" component="h1" fontWeight="bold">
            {scenario.name || 'Untitled Scenario'}
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            {property?.name || 'Property'} - {scenario.description || 'No description'}
          </Typography>
        </Box>
        
        <Box>
          <Button 
            variant="outlined" 
            color="primary" 
            startIcon={<EditIcon />} 
            onClick={handleEditScenario}
            sx={{ mr: 2 }}
          >
            Edit
          </Button>
          
          <Button 
            variant="contained" 
            color="primary" 
            startIcon={<CalculateIcon />} 
            onClick={handleRunAnalysis}
            disabled={analyzing}
          >
            {analyzing ? 'Analyzing...' : 'Run Analysis'}
          </Button>
        </Box>
      </Box>
      
      {analyzing && (
        <Paper sx={{ p: 2, mb: 3, backgroundColor: 'primary.light', color: 'primary.contrastText' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Box sx={{ width: '100%', mr: 1 }}>
              <Typography variant="body1" fontWeight="medium">
                Analysis in progress... This may take a few moments.
              </Typography>
            </Box>
            <Box sx={{ minWidth: 35 }}>
              <CircularProgress size={24} color="inherit" />
            </Box>
          </Box>
          <LinearProgress color="inherit" sx={{ mt: 1 }} />
        </Paper>
      )}
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      {scenario.status === 'error' && (
        <Alert severity="error" sx={{ mb: 3 }}>
          The last analysis encountered an error. Please try running the analysis again.
        </Alert>
      )}
      
      {scenario.is_baseline && (
        <Chip 
          label="Baseline Scenario" 
          color="primary" 
          sx={{ mb: 3 }}
        />
      )}
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs 
          value={activeTab} 
          onChange={handleTabChange}
          aria-label="scenario tabs"
        >
          <Tab label="Overview" id="scenario-tab-0" aria-controls="scenario-tabpanel-0" />
          <Tab label="Parameters" id="scenario-tab-1" aria-controls="scenario-tabpanel-1" />
        </Tabs>
      </Box>
      
      <Box
        role="tabpanel"
        hidden={activeTab !== 0}
        id="scenario-tabpanel-0"
        aria-labelledby="scenario-tab-0"
      >
        {activeTab === 0 && renderOverview()}
      </Box>
      
      <Box
        role="tabpanel"
        hidden={activeTab !== 1}
        id="scenario-tabpanel-1"
        aria-labelledby="scenario-tab-1"
      >
        {activeTab === 1 && renderParameters()}
      </Box>
    </Box>
  );
};

export default ScenarioDetail;