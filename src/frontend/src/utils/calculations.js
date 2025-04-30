/**
 * Calculate the monthly mortgage payment based on loan amount, interest rate, and repayment rate
 * @param {number} loanAmount - The loan amount
 * @param {number} interestRate - Annual interest rate (%)
 * @param {number} repaymentRate - Annual repayment rate (%)
 * @returns {number} Monthly payment amount
 */
export const calculateMonthlyPayment = (loanAmount, interestRate, repaymentRate) => {
  // Convert annual rates to monthly rates
  const monthlyInterestRate = interestRate / 100 / 12;
  const monthlyRepaymentRate = repaymentRate / 100 / 12;
  
  // Calculate total monthly rate (interest + repayment)
  const totalMonthlyRate = monthlyInterestRate + monthlyRepaymentRate;
  
  // Calculate monthly payment
  return loanAmount * totalMonthlyRate;
};

/**
 * Calculate cash flow for a property investment
 * @param {number} rentalIncome - Monthly rental income
 * @param {number} expenses - Monthly operating expenses
 * @param {number} mortgagePayment - Monthly mortgage payment
 * @param {number} taxSavings - Monthly tax savings
 * @returns {Object} Cash flow data (monthly and annual)
 */
export const calculateCashFlow = (rentalIncome, expenses, mortgagePayment, taxSavings) => {
  // Calculate monthly cash flows
  const monthlyCashFlowBeforeTax = rentalIncome - expenses - mortgagePayment;
  const monthlyCashFlowAfterTax = monthlyCashFlowBeforeTax + taxSavings;
  
  // Calculate annual amounts
  const annualIncome = rentalIncome * 12;
  const annualExpenses = expenses * 12;
  const annualMortgage = mortgagePayment * 12;
  const annualTaxSavings = taxSavings * 12;
  const annualCashFlowBeforeTax = monthlyCashFlowBeforeTax * 12;
  const annualCashFlowAfterTax = monthlyCashFlowAfterTax * 12;
  
  return {
    monthlyIncome: rentalIncome,
    monthlyExpenses: expenses,
    monthlyMortgage: mortgagePayment,
    monthlyTaxSavings: taxSavings,
    monthlyCashFlowBeforeTax,
    monthlyCashFlowAfterTax,
    annualIncome,
    annualExpenses,
    annualMortgage,
    annualTaxSavings,
    annualCashFlowBeforeTax,
    annualCashFlowAfterTax
  };
};

/**
 * Calculate investment metrics (Cap Rate, Cash on Cash Return, ROI, etc.)
 * @param {number} purchasePrice - Property purchase price
 * @param {number} closingCosts - Total closing costs
 * @param {number} downPayment - Down payment amount
 * @param {number} annualIncome - Annual rental income
 * @param {number} annualExpenses - Annual operating expenses
 * @param {number} annualCashFlow - Annual cash flow after tax
 * @returns {Object} Investment metrics
 */
export const calculateInvestmentMetrics = (
  purchasePrice,
  closingCosts,
  downPayment,
  annualIncome,
  annualExpenses,
  annualCashFlow
) => {
  // Calculate total investment
  const totalInvestment = purchasePrice + closingCosts;
  
  // Calculate total cash invested
  const totalCashInvested = downPayment + closingCosts;
  
  // Calculate Net Operating Income (NOI)
  const noi = annualIncome - annualExpenses;
  
  // Calculate Cap Rate
  const capRate = (noi / purchasePrice) * 100;
  
  // Calculate Cash on Cash Return
  const cashOnCash = (annualCashFlow / totalCashInvested) * 100;
  
  // Calculate Return on Investment (ROI)
  // Assuming 3% annual appreciation for simplicity; this could be passed as a parameter
  const annualAppreciation = 0.03;
  const propertyValueAppreciation = purchasePrice * annualAppreciation;
  const totalAnnualReturn = annualCashFlow + propertyValueAppreciation;
  const roi = (totalAnnualReturn / totalInvestment) * 100;
  
  // Calculate Debt Service Coverage Ratio (DSCR)
  const annualMortgage = (annualIncome - annualExpenses - annualCashFlow);
  const dscr = annualMortgage > 0 ? noi / annualMortgage : 0;
  
  return {
    totalInvestment,
    totalCashInvested,
    noi,
    capRate,
    cashOnCash,
    roi,
    dscr
  };
};

/**
 * Calculate the total cost of acquisition including purchase price and closing costs
 * @param {number} purchasePrice - Property purchase price
 * @param {Object} closingCosts - Closing cost components
 * @returns {number} Total acquisition cost
 */
export const calculateTotalAcquisitionCost = (purchasePrice, closingCosts) => {
  return purchasePrice + Object.values(closingCosts).reduce((sum, value) => sum + value, 0);
};

/**
 * Calculate the total annual depreciation for tax purposes
 * @param {number} buildingValue - Value of the building (excluding land)
 * @param {number} depreciationPeriod - Depreciation period in years (e.g., 27.5 for residential in the US)
 * @returns {number} Annual depreciation amount
 */
export const calculateDepreciation = (buildingValue, depreciationPeriod) => {
  return buildingValue / depreciationPeriod;
};

/**
 * Calculate tax savings based on taxable income, tax rate, and deductions
 * @param {number} taxRate - Marginal tax rate as a percentage
 * @param {number} deductions - Total tax deductions
 * @returns {number} Tax savings
 */
export const calculateTaxSavings = (taxRate, deductions) => {
  return (taxRate / 100) * deductions;
};