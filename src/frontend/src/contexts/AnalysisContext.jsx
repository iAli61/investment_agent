import React, { createContext, useContext, useState, useEffect } from 'react';
import { useProperty } from './PropertyContext';
import { useUnits } from './UnitsContext';
import { useFinancing } from './FinancingContext';
import { useExpensesAndTax } from './ExpensesAndTaxContext';

// Initial state for analysis data
const initialAnalysisState = {
  // Cash flow analysis
  monthlyCashFlow: 0,
  annualCashFlow: 0,
  cashOnCashReturn: 0,
  capRate: 0,
  
  // Tax analysis
  beforeTaxCashFlow: 0,
  afterTaxCashFlow: 0,
  taxSavings: 0,
  
  // Long-term analysis
  propertyAppreciationRate: 3, // 3% annual appreciation
  projectedValue: {},
  returnOnInvestment: 0,
  breakEvenPoint: 0,
  
  // Risk metrics
  debtServiceCoverageRatio: 0,
  vacancyBreakEven: 0,
  
  // Investment metrics
  totalInvestment: 0,
  cashNeededToClose: 0,
  
  // Advanced calculations
  fiveYearProjections: [],
  tenYearProjections: [],
  thirtyYearProjections: [],
  
  // Analysis status
  isAnalysisComplete: false,
  lastUpdated: null
};

// Create the context
const AnalysisContext = createContext();

// Provider component
export const AnalysisProvider = ({ children }) => {
  const { property } = useProperty();
  const { units, totalRentalIncome } = useUnits();
  const { financing } = useFinancing();
  const { expensesAndTax } = useExpensesAndTax();
  const [analysis, setAnalysis] = useState(initialAnalysisState);

  // Run full analysis when property, units, financing or expenses data changes
  useEffect(() => {
    if (property.purchasePrice > 0 && units.length > 0) {
      performFullAnalysis();
    }
  }, [property, units, totalRentalIncome, financing, expensesAndTax]);

  // Perform comprehensive investment analysis
  const performFullAnalysis = () => {
    // Calculate cash flow
    const monthlyCashFlow = calculateMonthlyCashFlow();
    const annualCashFlow = monthlyCashFlow * 12;
    
    // Calculate investment returns
    const totalInvestment = financing.downPayment + property.closingCosts;
    const cashOnCashReturn = totalInvestment > 0 ? 
                             (annualCashFlow / totalInvestment) * 100 : 0;
    
    // Calculate debt service coverage ratio
    const debtServiceCoverageRatio = financing.monthlyPayment > 0 ?
                                     (totalRentalIncome - expensesAndTax.totalOperatingExpenses) / 
                                     financing.monthlyPayment : 0;
    
    // Calculate tax benefits
    const taxSavings = calculateTaxSavings();
    const afterTaxCashFlow = annualCashFlow + taxSavings;
    
    // Calculate vacancy break-even
    const vacancyBreakEven = calculateVacancyBreakEven();
    
    // Generate projections
    const fiveYearProjections = generateProjections(5);
    const tenYearProjections = generateProjections(10);
    const thirtyYearProjections = generateProjections(30);
    
    // Calculate projected property value (5 years)
    const projectedValue = {
      fiveYear: calculateProjectedValue(5),
      tenYear: calculateProjectedValue(10),
      thirtyYear: calculateProjectedValue(30)
    };
    
    // Calculate return on investment (including appreciation and equity)
    const returnOnInvestment = calculateROI(5); // 5-year ROI
    
    // Update analysis state
    setAnalysis({
      ...analysis,
      monthlyCashFlow,
      annualCashFlow,
      cashOnCashReturn,
      capRate: expensesAndTax.capRate,
      beforeTaxCashFlow: annualCashFlow,
      afterTaxCashFlow,
      taxSavings,
      projectedValue,
      returnOnInvestment,
      debtServiceCoverageRatio,
      vacancyBreakEven,
      totalInvestment,
      cashNeededToClose: totalInvestment,
      fiveYearProjections,
      tenYearProjections,
      thirtyYearProjections,
      isAnalysisComplete: true,
      lastUpdated: new Date().toISOString()
    });
  };

  // Calculate monthly cash flow (income - expenses - mortgage)
  const calculateMonthlyCashFlow = () => {
    return totalRentalIncome - 
           expensesAndTax.totalOperatingExpenses - 
           financing.monthlyPayment;
  };

  // Calculate tax savings from depreciation and interest deductions
  const calculateTaxSavings = () => {
    const { depreciationAmount, taxRate, interestDeduction } = expensesAndTax;
    const annualInterest = interestDeduction ? getAnnualInterest() : 0;
    return (depreciationAmount + annualInterest) * (taxRate / 100);
  };

  // Get annual interest paid (first year)
  const getAnnualInterest = () => {
    // Simple estimate if amortization schedule not available
    if (!financing.amortizationSchedule || financing.amortizationSchedule.length === 0) {
      return financing.loanAmount * (financing.interestRate / 100);
    }
    
    // Get from amortization schedule
    const firstYearSchedule = financing.amortizationSchedule.slice(0, 1);
    return firstYearSchedule.reduce((sum, payment) => sum + payment.interestPayment, 0);
  };

  // Calculate vacancy break-even percentage
  const calculateVacancyBreakEven = () => {
    const operatingExpensesExcludingVacancy = 
      expensesAndTax.totalOperatingExpenses - 
      (expensesAndTax.vacancy / 100) * totalRentalIncome;
    
    const availableForVacancy = totalRentalIncome - operatingExpensesExcludingVacancy - financing.monthlyPayment;
    
    return totalRentalIncome > 0 ? 
           (availableForVacancy / totalRentalIncome) * 100 : 0;
  };

  // Generate cash flow projections for specified number of years
  const generateProjections = (years) => {
    const projections = [];
    let currentValue = property.purchasePrice;
    let currentRent = totalRentalIncome;
    
    for (let year = 1; year <= years; year++) {
      // Increase property value by appreciation rate
      currentValue *= (1 + analysis.propertyAppreciationRate / 100);
      
      // Increase rent by 2% per year (conservative estimate)
      currentRent *= 1.02;
      
      // Calculate loan balance at this point
      const loanBalanceIndex = Math.min(year, financing.amortizationSchedule.length - 1);
      const loanBalance = financing.amortizationSchedule[loanBalanceIndex]?.remainingBalance || 0;
      
      // Calculate equity
      const equity = currentValue - loanBalance;
      
      // Calculate cash flow
      const yearlyExpenses = expensesAndTax.totalOperatingExpenses * 12 * Math.pow(1.02, year - 1); // 2% annual increase
      const yearlyCashFlow = (currentRent * 12) - yearlyExpenses - (financing.monthlyPayment * 12);
      
      projections.push({
        year,
        propertyValue: currentValue,
        equity,
        rentalIncome: currentRent * 12,
        cashFlow: yearlyCashFlow,
        loanBalance
      });
    }
    
    return projections;
  };

  // Calculate projected property value after specified years
  const calculateProjectedValue = (years) => {
    return property.purchasePrice * Math.pow(1 + analysis.propertyAppreciationRate / 100, years);
  };

  // Calculate ROI over specified years (includes cash flow, appreciation, and equity)
  const calculateROI = (years) => {
    if (analysis.totalInvestment <= 0) return 0;
    
    // Get the projection for the specified year
    const projections = generateProjections(years);
    const finalYear = projections[years - 1];
    
    if (!finalYear) return 0;
    
    // Calculate total return (cash flow + appreciation + equity)
    const totalCashFlow = projections.reduce((sum, year) => sum + year.cashFlow, 0);
    const appreciation = finalYear.propertyValue - property.purchasePrice;
    const equityGain = finalYear.equity - financing.downPayment;
    
    const totalReturn = totalCashFlow + appreciation + equityGain;
    const annualizedROI = Math.pow(1 + (totalReturn / analysis.totalInvestment), 1/years) - 1;
    
    return annualizedROI * 100; // Convert to percentage
  };

  // Update analysis parameters
  const updateAnalysis = (updates) => {
    setAnalysis(prev => ({ ...prev, ...updates }));
  };

  // Reset analysis data
  const resetAnalysis = () => {
    setAnalysis(initialAnalysisState);
  };

  // Value object to be provided
  const value = {
    analysis,
    updateAnalysis,
    resetAnalysis,
    performFullAnalysis
  };

  return (
    <AnalysisContext.Provider value={value}>
      {children}
    </AnalysisContext.Provider>
  );
};

// Custom hook for accessing the context
export const useAnalysis = () => {
  const context = useContext(AnalysisContext);
  if (context === undefined) {
    throw new Error('useAnalysis must be used within an AnalysisProvider');
  }
  return context;
};

export default AnalysisContext;