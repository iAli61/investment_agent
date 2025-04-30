import React, { createContext, useContext, useState, useEffect } from 'react';
import { useProperty } from './PropertyContext';

// Initial state for a single unit
const initialUnitState = {
  id: '',
  name: '',
  area: 0,
  bedrooms: 1,
  bathrooms: 1,
  monthlyRent: 0,
  isRented: false,
  tenantName: '',
  leaseStartDate: '',
  leaseEndDate: '',
  notes: ''
};

// Create the context
const UnitsContext = createContext();

// Provider component
export const UnitsProvider = ({ children }) => {
  const [units, setUnits] = useState([]);
  const [totalRentalIncome, setTotalRentalIncome] = useState(0);
  const { property } = useProperty();

  // Generate a unique ID for a new unit
  const generateUnitId = () => {
    return `unit_${new Date().getTime()}_${Math.floor(Math.random() * 1000)}`;
  };

  // Add a new rental unit
  const addUnit = (unitData = {}) => {
    const newUnit = {
      ...initialUnitState,
      ...unitData,
      id: generateUnitId()
    };
    
    setUnits(prevUnits => [...prevUnits, newUnit]);
  };

  // Update an existing unit
  const updateUnit = (id, updates) => {
    setUnits(prevUnits => 
      prevUnits.map(unit => 
        unit.id === id ? { ...unit, ...updates } : unit
      )
    );
  };

  // Remove a unit
  const removeUnit = (id) => {
    setUnits(prevUnits => prevUnits.filter(unit => unit.id !== id));
  };

  // Recalculate total rental income whenever units change
  useEffect(() => {
    const total = units.reduce((sum, unit) => sum + (unit.monthlyRent || 0), 0);
    setTotalRentalIncome(total);
  }, [units]);

  // Create a default unit if property exists but no units
  useEffect(() => {
    if (property && property.address && units.length === 0) {
      // Create a default unit based on property details
      addUnit({
        name: 'Main Unit',
        area: property.totalArea,
        monthlyRent: estimateRent(property.totalArea, property.city)
      });
    }
  }, [property]);

  // Simple function to estimate rent based on area and location
  // This would be replaced with more sophisticated logic in a real app
  const estimateRent = (area, city) => {
    // Default rates per square meter (very simplified)
    const ratesByCity = {
      'Berlin': 15,
      'Munich': 20,
      'Hamburg': 14,
      'Frankfurt': 16,
      'Cologne': 12,
      'default': 10
    };
    
    const ratePerSqm = ratesByCity[city] || ratesByCity.default;
    return Math.round(area * ratePerSqm);
  };

  // Value object to be provided
  const value = {
    units,
    totalRentalIncome,
    addUnit,
    updateUnit,
    removeUnit
  };

  return (
    <UnitsContext.Provider value={value}>
      {children}
    </UnitsContext.Provider>
  );
};

// Custom hook for accessing the context
export const useUnits = () => {
  const context = useContext(UnitsContext);
  if (context === undefined) {
    throw new Error('useUnits must be used within a UnitsProvider');
  }
  return context;
};

export default UnitsContext;