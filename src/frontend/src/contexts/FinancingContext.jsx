import React, { createContext, useContext, useState, useEffect } from 'react';
import { useProperty } from './PropertyContext';

// Initial state for financing data
const initialFinancingState = {
  downPayment: 0,
  downPaymentPercentage: 20, // 20%
  loanAmount: 0,
  interestRate: 3.5, // 3.5%
  loanTerm: 30, // 30 years
  paymentFrequency: 'monthly',
  startDate: new Date().toISOString().split('T')[0],
  additionalPayments: 0,
  monthlyPayment: 0,
  totalInterest: 0,
  totalPayments: 0,
  amortizationSchedule: []
};

// Create the context
const FinancingContext = createContext();

// Provider component
export const FinancingProvider = ({ children }) => {
  const { property } = useProperty();
  const [financing, setFinancing] = useState(initialFinancingState);

  // Calculate mortgage details when property or financing values change
  useEffect(() => {
    if (property && property.purchasePrice) {
      updateFinancingCalculations();
    }
  }, [property, financing.downPaymentPercentage, financing.interestRate, financing.loanTerm]);

  // Update financing data
  const updateFinancing = (updates) => {
    setFinancing(prev => {
      let newState = { ...prev, ...updates };
      
      // If downPayment was updated, recalculate downPaymentPercentage
      if (updates.downPayment !== undefined && property.purchasePrice) {
        newState.downPaymentPercentage = (updates.downPayment / property.purchasePrice) * 100;
      }
      
      // If downPaymentPercentage was updated, recalculate downPayment
      if (updates.downPaymentPercentage !== undefined && property.purchasePrice) {
        newState.downPayment = (updates.downPaymentPercentage / 100) * property.purchasePrice;
      }
      
      return newState;
    });
  };

  // Calculate loan amount, monthly payment, and amortization schedule
  const updateFinancingCalculations = () => {
    const { purchasePrice } = property;
    const { downPaymentPercentage, interestRate, loanTerm } = financing;
    
    // Calculate down payment and loan amount
    const downPayment = (downPaymentPercentage / 100) * purchasePrice;
    const loanAmount = purchasePrice - downPayment;
    
    // Calculate monthly payment using the mortgage formula
    // M = P[r(1+r)^n]/[(1+r)^n-1]
    const monthlyRate = interestRate / 100 / 12;
    const totalPayments = loanTerm * 12;
    let monthlyPayment = 0;
    
    if (monthlyRate > 0) {
      monthlyPayment = loanAmount * 
        (monthlyRate * Math.pow(1 + monthlyRate, totalPayments)) / 
        (Math.pow(1 + monthlyRate, totalPayments) - 1);
    } else {
      monthlyPayment = loanAmount / totalPayments;
    }
    
    // Calculate total interest
    const totalPaid = monthlyPayment * totalPayments;
    const totalInterest = totalPaid - loanAmount;
    
    // Generate amortization schedule
    const schedule = generateAmortizationSchedule(
      loanAmount, 
      monthlyRate, 
      totalPayments, 
      monthlyPayment
    );
    
    // Update state with calculations
    setFinancing(prev => ({
      ...prev,
      downPayment,
      loanAmount,
      monthlyPayment,
      totalInterest,
      totalPayments: totalPaid,
      amortizationSchedule: schedule
    }));
  };
  
  // Generate amortization schedule (simplified version)
  const generateAmortizationSchedule = (loanAmount, monthlyRate, totalPayments, monthlyPayment) => {
    const schedule = [];
    let balance = loanAmount;
    let totalInterestPaid = 0;
    let totalPrincipalPaid = 0;
    
    for (let payment = 1; payment <= Math.min(totalPayments, 360); payment++) {
      // Calculate interest and principal for this payment
      const interestPayment = balance * monthlyRate;
      const principalPayment = monthlyPayment - interestPayment;
      
      // Update running totals
      totalInterestPaid += interestPayment;
      totalPrincipalPaid += principalPayment;
      balance -= principalPayment;
      
      // Add to schedule if it's a significant payment (e.g., yearly)
      if (payment % 12 === 0 || payment === 1 || payment === totalPayments) {
        schedule.push({
          payment,
          date: new Date(new Date().setMonth(new Date().getMonth() + payment)).toISOString().split('T')[0],
          monthlyPayment,
          interestPayment,
          principalPayment,
          totalInterestPaid,
          totalPrincipalPaid,
          remainingBalance: Math.max(0, balance)
        });
      }
    }
    
    return schedule;
  };

  // Reset financing data
  const resetFinancing = () => {
    setFinancing(initialFinancingState);
  };

  // Value object to be provided
  const value = {
    financing,
    updateFinancing,
    resetFinancing
  };

  return (
    <FinancingContext.Provider value={value}>
      {children}
    </FinancingContext.Provider>
  );
};

// Custom hook for accessing the context
export const useFinancing = () => {
  const context = useContext(FinancingContext);
  if (context === undefined) {
    throw new Error('useFinancing must be used within a FinancingProvider');
  }
  return context;
};

export default FinancingContext;