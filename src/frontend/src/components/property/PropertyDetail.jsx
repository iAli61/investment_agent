import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  Tabs, 
  Tab, 
  Button, 
  CircularProgress,
  Alert,
  Grid,
  Divider,
  Chip
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import EditIcon from '@mui/icons-material/Edit';
import AddIcon from '@mui/icons-material/Add';
import CompareArrowsIcon from '@mui/icons-material/CompareArrows';
import apiService from '../../services/api';

/**
 * PropertyDetail component for displaying detailed property information and scenarios
 */
const PropertyDetail = () => {
  const { propertyId } = useParams();
  const navigate = useNavigate();
  const [property, setProperty] = useState(null);
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenarios, setSelectedScenarios] = useState([]);
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [scenariosLoading, setScenariosLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch property data when component mounts or propertyId changes
  useEffect(() => {
    fetchPropertyData();
  }, [propertyId]);

  /**
   * Fetch property details and scenarios
   */
  const fetchPropertyData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch property details
      const propertyData = await apiService.getPropertyById(propertyId);
      setProperty(propertyData);
      
      // Fetch scenarios for the property
      setScenariosLoading(true);
      const scenariosData = await apiService.getPropertyScenarios(propertyId);
      setScenarios(scenariosData || []);
      setScenariosLoading(false);
    } catch (err) {
      console.error('Error fetching property data:', err);
      setError('Failed to load property data. Please try again later.');
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
   * Navigate to edit property page
   */
  const handleEditProperty = () => {
    navigate(`/properties/${propertyId}/edit`);
  };

  /**
   * Navigate to create scenario page
   */
  const handleCreateScenario = () => {
    navigate(`/properties/${propertyId}/scenarios/new`);
  };

  /**
   * Navigate to scenario detail page
   * @param {number} scenarioId - ID of the scenario to view
   */
  const handleViewScenario = (scenarioId) => {
    navigate(`/properties/${propertyId}/scenarios/${scenarioId}`);
  };

  /**
   * Toggle scenario selection for comparison
   * @param {number} scenarioId - ID of the scenario to toggle
   */
  const handleToggleScenarioSelection = (scenarioId) => {
    setSelectedScenarios(prev => {
      if (prev.includes(scenarioId)) {
        return prev.filter(id => id !== scenarioId);
      } else {
        return [...prev, scenarioId];
      }
    });
  };

  /**
   * Navigate to scenario comparison page
   */
  const handleCompareScenarios = () => {
    if (selectedScenarios.length >= 2) {
      navigate(`/properties/${propertyId}/scenarios/compare?ids=${selectedScenarios.join(',')}`);
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

  // Property overview tab content
  const renderPropertyOverview = () => {
    if (!property) return null;
    
    const { property_details } = property;
    
    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Property Details
              </Typography>
              
              <Box sx={{ mt: 2 }}>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Property Type</Typography>
                    <Typography variant="body1">
                      {property_details?.property_type || 'N/A'}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Year Built</Typography>
                    <Typography variant="body1">
                      {property_details?.year_built || 'N/A'}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Square Footage</Typography>
                    <Typography variant="body1">
                      {property_details?.square_footage 
                        ? `${property_details.square_footage.toLocaleString()} sq ft` 
                        : 'N/A'}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Lot Size</Typography>
                    <Typography variant="body1">
                      {property_details?.lot_size 
                        ? `${property_details.lot_size.toLocaleString()} sq ft` 
                        : 'N/A'}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Bedrooms</Typography>
                    <Typography variant="body1">
                      {property_details?.bedrooms || 'N/A'}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Bathrooms</Typography>
                    <Typography variant="body1">
                      {property_details?.bathrooms || 'N/A'}
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Financial Overview
              </Typography>
              
              <Box sx={{ mt: 2 }}>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Purchase Price</Typography>
                    <Typography variant="body1" fontWeight="medium">
                      {formatCurrency(property_details?.purchase_price)}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Current Value</Typography>
                    <Typography variant="body1" fontWeight="medium">
                      {formatCurrency(property_details?.current_value)}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Monthly Rent</Typography>
                    <Typography variant="body1">
                      {formatCurrency(property_details?.monthly_rent)}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Monthly Expenses</Typography>
                    <Typography variant="body1">
                      {formatCurrency(property_details?.monthly_expenses)}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Cash Flow</Typography>
                    <Typography 
                      variant="body1" 
                      color={
                        property_details?.cash_flow > 0 
                          ? 'success.main' 
                          : property_details?.cash_flow < 0 
                            ? 'error.main' 
                            : 'text.primary'
                      }
                      fontWeight="medium"
                    >
                      {formatCurrency(property_details?.cash_flow)}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Cap Rate</Typography>
                    <Typography variant="body1">
                      {formatPercentage(property_details?.cap_rate)}
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
            </Grid>
            
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                Location
              </Typography>
              
              <Box sx={{ mt: 2 }}>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">Address</Typography>
                    <Typography variant="body1">
                      {property_details?.address?.street}
                    </Typography>
                    <Typography variant="body1">
                      {property_details?.address?.city}, {property_details?.address?.state} {property_details?.address?.zip_code}
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    );
  };

  // Scenarios tab content
  const renderScenarios = () => {
    return (
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box>
            <Button 
              variant="contained" 
              color="primary" 
              startIcon={<AddIcon />} 
              onClick={handleCreateScenario}
              sx={{ mr: 2 }}
            >
              Create Scenario
            </Button>
            
            <Button 
              variant="outlined" 
              color="primary" 
              startIcon={<CompareArrowsIcon />} 
              onClick={handleCompareScenarios}
              disabled={selectedScenarios.length < 2}
            >
              Compare Selected ({selectedScenarios.length})
            </Button>
          </Box>
        </Box>
        
        {scenariosLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        ) : scenarios.length === 0 ? (
          <Card sx={{ mb: 3, textAlign: 'center', p: 3, backgroundColor: 'background.paper' }}>
            <CardContent>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No Scenarios Found
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                Create your first investment scenario for this property.
              </Typography>
              <Button 
                variant="contained" 
                color="primary" 
                startIcon={<AddIcon />} 
                onClick={handleCreateScenario}
              >
                Create Your First Scenario
              </Button>
            </CardContent>
          </Card>
        ) : (
          <Grid container spacing={3}>
            {scenarios.map((scenario) => (
              <Grid item xs={12} md={6} key={scenario.id}>
                <Card 
                  sx={{ 
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    position: 'relative',
                    outline: selectedScenarios.includes(scenario.id) 
                      ? '2px solid' 
                      : 'none',
                    outlineColor: 'primary.main',
                    transition: 'outline 0.2s ease',
                  }}
                >
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="h6" component="h2" fontWeight="bold">
                        {scenario.name}
                      </Typography>
                      
                      {scenario.is_baseline && (
                        <Chip 
                          label="Baseline" 
                          color="primary" 
                          size="small"
                        />
                      )}
                    </Box>
                    
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {scenario.description || 'No description provided.'}
                    </Typography>
                    
                    <Divider sx={{ my: 2 }} />
                    
                    <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                      Key Metrics
                    </Typography>
                    
                    <Grid container spacing={1}>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">Cash on Cash Return:</Typography>
                        <Typography variant="body1" fontWeight="medium">
                          {formatPercentage(scenario.results?.cash_on_cash_return)}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">Cap Rate:</Typography>
                        <Typography variant="body1" fontWeight="medium">
                          {formatPercentage(scenario.results?.cap_rate)}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">Monthly Cash Flow:</Typography>
                        <Typography variant="body1" fontWeight="medium" color={
                          (scenario.results?.monthly_cash_flow || 0) > 0 
                            ? 'success.main' 
                            : (scenario.results?.monthly_cash_flow || 0) < 0 
                              ? 'error.main' 
                              : 'text.primary'
                        }>
                          {formatCurrency(scenario.results?.monthly_cash_flow)}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">IRR (5yr):</Typography>
                        <Typography variant="body1" fontWeight="medium">
                          {formatPercentage(scenario.results?.irr_5year)}
                        </Typography>
                      </Grid>
                    </Grid>
                    
                    <Divider sx={{ my: 2 }} />
                    
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" color="text.secondary">Status:</Typography>
                      <Chip 
                        label={scenario.status?.toUpperCase()} 
                        color={
                          scenario.status === 'completed' 
                            ? 'success' 
                            : scenario.status === 'analyzing' 
                              ? 'warning' 
                              : scenario.status === 'error' 
                                ? 'error' 
                                : 'default'
                        }
                        size="small"
                      />
                    </Box>
                  </CardContent>
                  
                  <Box sx={{ display: 'flex', p: 2, pt: 0, justifyContent: 'space-between' }}>
                    <Button
                      variant="outlined"
                      color={selectedScenarios.includes(scenario.id) ? 'primary' : 'inherit'}
                      size="small"
                      onClick={() => handleToggleScenarioSelection(scenario.id)}
                    >
                      {selectedScenarios.includes(scenario.id) ? 'Selected' : 'Select'}
                    </Button>
                    
                    <Button
                      variant="contained"
                      color="primary"
                      size="small"
                      onClick={() => handleViewScenario(scenario.id)}
                    >
                      View Details
                    </Button>
                  </Box>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Box>
    );
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 3 }}>
        {error}
      </Alert>
    );
  }

  if (!property) {
    return (
      <Alert severity="info" sx={{ mt: 3 }}>
        Property not found.
      </Alert>
    );
  }

  return (
    <Box sx={{ py: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" component="h1" fontWeight="bold">
            {property.name || 'Untitled Property'}
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            {property.property_details?.address?.street}, {property.property_details?.address?.city}, {property.property_details?.address?.state}
          </Typography>
        </Box>
        
        <Button 
          variant="outlined" 
          color="primary" 
          startIcon={<EditIcon />} 
          onClick={handleEditProperty}
        >
          Edit Property
        </Button>
      </Box>
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs 
          value={activeTab} 
          onChange={handleTabChange}
          aria-label="property tabs"
        >
          <Tab label="Overview" id="property-tab-0" aria-controls="property-tabpanel-0" />
          <Tab label="Scenarios" id="property-tab-1" aria-controls="property-tabpanel-1" />
        </Tabs>
      </Box>
      
      <Box
        role="tabpanel"
        hidden={activeTab !== 0}
        id="property-tabpanel-0"
        aria-labelledby="property-tab-0"
      >
        {activeTab === 0 && renderPropertyOverview()}
      </Box>
      
      <Box
        role="tabpanel"
        hidden={activeTab !== 1}
        id="property-tabpanel-1"
        aria-labelledby="property-tab-1"
      >
        {activeTab === 1 && renderScenarios()}
      </Box>
    </Box>
  );
};

export default PropertyDetail;