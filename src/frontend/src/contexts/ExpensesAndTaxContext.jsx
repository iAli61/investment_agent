import React, { createContext, useContext, useState, useEffect } from 'react';
import { useProperty } from './PropertyContext';
import { useUnits } from './UnitsContext';

// Initial state for expenses and tax data
const initialExpensesAndTaxState = {
  // Operating expenses
  propertyTax: 0,
  insurance: 0,
  maintenance: 0,
  utilities: 0,
  propertyManagement: 0,
  vacancy: 5, // 5% vacancy rate
  other: 0,
  totalOperatingExpenses: 0,
  
  // Tax deductions
  depreciationPeriod: 27.5, // years (residential real estate standard)
  depreciationAmount: 0,
  interestDeduction: true,
  taxRate: 25, // personal income tax rate
  
  // Calculations
  netOperatingIncome: 0,
  cashFlow: 0,
  capRate: 0,
  cashOnCashReturn: 0,
  afterTaxCashFlow: 0
};

// Create the context
const ExpensesAndTaxContext = createContext();

// Provider component
export const ExpensesAndTaxProvider = ({ children }) => {
  const { property } = useProperty();
  const { totalRentalIncome } = useUnits();
  const [expensesAndTax, setExpensesAndTax] = useState(initialExpensesAndTaxState);

  // Update expenses and tax data
  const updateExpensesAndTax = (updates) => {
    setExpensesAndTax(prev => ({ ...prev, ...updates }));
  };

  // Calculate derived values when inputs change
  useEffect(() => {
    if (property.purchasePrice > 0) {
      calculateFinancialMetrics();
    }
  }, [property, totalRentalIncome, expensesAndTax]);

  // Calculate all financial metrics
  const calculateFinancialMetrics = () => {
    // Extract values needed for calculations
    const {
      propertyTax, 
      insurance, 
      maintenance, 
      utilities, 
      propertyManagement, 
      vacancy, 
      other,
      depreciationPeriod,
      taxRate
    } = expensesAndTax;

    // Calculate total operating expenses
    const vacancyAmount = (vacancy / 100) * totalRentalIncome;
    const totalOpEx = propertyTax + insurance + maintenance + utilities + 
                      propertyManagement + vacancyAmount + other;

    // Calculate net operating income
    const netOperatingIncome = totalRentalIncome - totalOpEx;

    // Calculate cap rate
    const capRate = property.purchasePrice > 0 ? 
                    (netOperatingIncome / property.purchasePrice) * 100 : 0;

    // Calculate depreciation (building value only, typically 80% of property value)
    const buildingValue = property.purchasePrice * 0.8;
    const annualDepreciation = buildingValue / depreciationPeriod;

    // Update state with calculations
    setExpensesAndTax(prev => ({
      ...prev,
      totalOperatingExpenses: totalOpEx,
      depreciationAmount: annualDepreciation,
      netOperatingIncome,
      capRate
      // Cash flow and cash-on-cash return will be calculated in a separate effect
      // that depends on financing data
    }));
  };

  // Reset expenses and tax data
  const resetExpensesAndTax = () => {
    setExpensesAndTax(initialExpensesAndTaxState);
  };

  // Value object to be provided
  const value = {
    expensesAndTax,
    updateExpensesAndTax,
    resetExpensesAndTax
  };

  return (
    <ExpensesAndTaxContext.Provider value={value}>
      {children}
    </ExpensesAndTaxContext.Provider>
  );
};

// Custom hook for accessing the context
export const useExpensesAndTax = () => {
  const context = useContext(ExpensesAndTaxContext);
  if (context === undefined) {
    throw new Error('useExpensesAndTax must be used within an ExpensesAndTaxProvider');
  }
  return context;
};

export default ExpensesAndTaxContext;