import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  CardActions, 
  Button, 
  Grid, 
  CircularProgress,
  Chip,
  Alert
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import HomeIcon from '@mui/icons-material/Home';
import ApartmentIcon from '@mui/icons-material/Apartment';
import apiService from '../../services/api';

/**
 * PropertyList component for displaying and managing properties
 * @param {Object} props - Component props
 * @param {number} props.userId - User ID for fetching properties
 */
const PropertyList = ({ userId }) => {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Fetch properties on component mount
  useEffect(() => {
    fetchProperties();
  }, [userId]);

  /**
   * Fetch all properties for the current user
   */
  const fetchProperties = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await apiService.getProperties(userId);
      setProperties(data || []);
    } catch (err) {
      console.error('Error fetching properties:', err);
      setError('Failed to load properties. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Navigate to property detail page
   * @param {number} propertyId - ID of the property to view
   */
  const handleViewProperty = (propertyId) => {
    navigate(`/properties/${propertyId}`);
  };

  /**
   * Navigate to create property page
   */
  const handleCreateProperty = () => {
    navigate('/properties/new');
  };

  /**
   * Get appropriate icon based on property type
   * @param {string} propertyType - Type of property
   * @returns {JSX.Element} Icon component
   */
  const getPropertyIcon = (propertyType) => {
    switch (propertyType?.toLowerCase()) {
      case 'multi-family':
      case 'apartment':
        return <ApartmentIcon fontSize="large" />;
      default:
        return <HomeIcon fontSize="large" />;
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

  return (
    <Box sx={{ py: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          My Properties
        </Typography>
        <Button 
          variant="contained" 
          color="primary" 
          startIcon={<AddIcon />} 
          onClick={handleCreateProperty}
        >
          Add Property
        </Button>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>
      ) : properties.length === 0 ? (
        <Card sx={{ mb: 3, textAlign: 'center', p: 3, backgroundColor: 'background.paper' }}>
          <CardContent>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No Properties Found
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
              Get started by adding your first investment property.
            </Typography>
            <Button 
              variant="contained" 
              color="primary" 
              startIcon={<AddIcon />} 
              onClick={handleCreateProperty}
            >
              Add Your First Property
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {properties.map((property) => (
            <Grid item xs={12} sm={6} md={4} key={property.id}>
              <Card 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 6
                  }
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Box sx={{ 
                      backgroundColor: 'primary.light', 
                      borderRadius: '50%', 
                      p: 1, 
                      mr: 2,
                      color: 'primary.contrastText'
                    }}>
                      {getPropertyIcon(property.property_details?.property_type)}
                    </Box>
                    <Box>
                      <Typography variant="h6" component="h2" fontWeight="bold">
                        {property.name || 'Untitled Property'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {property.property_details?.address?.city}, 
                        {property.property_details?.address?.state}
                      </Typography>
                    </Box>
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2" color="text.secondary">Purchase Price:</Typography>
                    <Typography variant="body1" fontWeight="medium">
                      {formatCurrency(property.property_details?.purchase_price)}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">Property Type:</Typography>
                    <Chip 
                      size="small" 
                      label={property.property_details?.property_type || 'N/A'} 
                      color="primary" 
                      variant="outlined"
                    />
                  </Box>
                  
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    {property.description || 'No description available.'}
                  </Typography>
                </CardContent>
                
                <CardActions sx={{ p: 2, pt: 0 }}>
                  <Button 
                    variant="contained" 
                    size="small" 
                    fullWidth
                    onClick={() => handleViewProperty(property.id)}
                  >
                    View Details
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};

export default PropertyList;