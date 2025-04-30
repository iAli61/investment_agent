import React, { createContext, useContext, useState } from 'react';

// Initial state for property data
const initialPropertyState = {
  address: '',
  city: '',
  postalCode: '',
  propertyType: 'apartment',
  purchasePrice: 0,
  constructionYear: new Date().getFullYear() - 30,
  totalArea: 0,
  lotSize: 0,
  purchaseDate: new Date().toISOString().split('T')[0],
  renovationCosts: 0,
  closingCosts: 0,
  additionalCosts: 0,
  totalInvestment: 0
};

// Create the context
const PropertyContext = createContext();

// Provider component
export const PropertyProvider = ({ children }) => {
  const [property, setProperty] = useState(initialPropertyState);

  // Calculate total investment
  const calculateTotalInvestment = (propertyData) => {
    const { purchasePrice, renovationCosts, closingCosts, additionalCosts } = propertyData;
    return (purchasePrice || 0) + 
           (renovationCosts || 0) + 
           (closingCosts || 0) + 
           (additionalCosts || 0);
  };

  // Update property data
  const updateProperty = (updates) => {
    setProperty(prev => {
      const newState = { ...prev, ...updates };
      newState.totalInvestment = calculateTotalInvestment(newState);
      return newState;
    });
  };

  // Reset property data
  const resetProperty = () => {
    setProperty(initialPropertyState);
  };

  // Value object to be provided
  const value = {
    property,
    updateProperty,
    resetProperty
  };

  return (
    <PropertyContext.Provider value={value}>
      {children}
    </PropertyContext.Provider>
  );
};

// Custom hook for accessing the context
export const useProperty = () => {
  const context = useContext(PropertyContext);
  if (context === undefined) {
    throw new Error('useProperty must be used within a PropertyProvider');
  }
  return context;
};

export default PropertyContext;