import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useExpensesAndTax } from '../contexts/ExpensesAndTaxContext';
import { useProperty } from '../contexts/PropertyContext';
import { useFinancing } from '../contexts/FinancingContext';
import { formatCurrency, formatPercent } from '../utils/formatters';
import InfoBox from '../components/common/InfoBox';
import MetricCard from '../components/common/MetricCard';

const ExpensesTaxPage = () => {
  const navigate = useNavigate();
  const { expenses, taxBenefits, updateOperatingExpenses, updateVacancyRate, updateTaxBenefits } = useExpensesAndTax();
  const { property } = useProperty();
  const { financing } = useFinancing();
  
  const [errors, setErrors] = useState({});
  const [activeTab, setActiveTab] = useState('expenses');

  // Check if prerequisite data exists, redirect if not
  useEffect(() => {
    if (!property.address) {
      navigate('/property-input');
    } else if (!financing.loanAmount) {
      navigate('/financing');
    }
  }, [property, financing, navigate]);

  // Handle expense input changes
  const handleExpenseChange = (e) => {
    const { name, value } = e.target;
    updateOperatingExpenses({ [name]: parseFloat(value) || 0 });
  };

  // Handle vacancy rate change
  const handleVacancyRateChange = (e) => {
    updateVacancyRate(parseFloat(e.target.value) || 0);
  };

  // Handle tax rate change
  const handleTaxRateChange = (e) => {
    updateTaxBenefits({ taxRate: parseFloat(e.target.value) || 0 });
  };

  // Handle depreciation changes
  const handleDepreciationChange = (e) => {
    const { name, value } = e.target;
    updateTaxBenefits({
      depreciation: {
        ...taxBenefits.depreciation,
        [name]: parseFloat(value) || 0
      }
    });
  };

  // Validate the form before submission
  const validateForm = () => {
    const newErrors = {};
    
    // Example validation - add more as needed
    if (expenses.vacancyRate < 0 || expenses.vacancyRate > 100) {
      newErrors.vacancyRate = 'Vacancy rate must be between 0% and 100%';
    }
    
    if (taxBenefits.taxRate < 0 || taxBenefits.taxRate > 100) {
      newErrors.taxRate = 'Tax rate must be between 0% and 100%';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (validateForm()) {
      navigate('/analysis-results');
    }
  };

  // Navigate back to previous step
  const handleBack = () => {
    navigate('/financing');
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Expenses & Tax Benefits</h1>
      
      {/* Tabs */}
      <div className="mb-6 border-b border-gray-200">
        <nav className="flex -mb-px">
          <button
            onClick={() => setActiveTab('expenses')}
            className={`${
              activeTab === 'expenses'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm`}
          >
            Operating Expenses
          </button>
          <button
            onClick={() => setActiveTab('tax')}
            className={`${
              activeTab === 'tax'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm`}
          >
            Tax Benefits
          </button>
        </nav>
      </div>
      
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <form onSubmit={handleSubmit}>
          {/* Operating Expenses Tab */}
          {activeTab === 'expenses' && (
            <div>
              <div className="mb-8">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-xl font-semibold">Regular Expenses</h2>
                  <div className="text-sm text-gray-600">
                    Annual Total: <span className="font-semibold">{formatCurrency(expenses.totalAnnualExpenses)}</span>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Property Tax */}
                  <div>
                    <label className="block text-gray-700 font-medium mb-2">Property Tax (Annual)</label>
                    <input
                      type="number"
                      name="propertyTax"
                      value={expenses.operatingExpenses.propertyTax}
                      onChange={handleExpenseChange}
                      min="0"
                      step="10"
                      className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  {/* Insurance */}
                  <div>
                    <label className="block text-gray-700 font-medium mb-2">Insurance (Annual)</label>
                    <input
                      type="number"
                      name="insurance"
                      value={expenses.operatingExpenses.insurance}
                      onChange={handleExpenseChange}
                      min="0"
                      step="10"
                      className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  {/* Management Fees */}
                  <div>
                    <label className="block text-gray-700 font-medium mb-2">Management Fees (Annual)</label>
                    <input
                      type="number"
                      name="managementFees"
                      value={expenses.operatingExpenses.managementFees}
                      onChange={handleExpenseChange}
                      min="0"
                      step="10"
                      className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  {/* Maintenance Reserve */}
                  <div>
                    <label className="block text-gray-700 font-medium mb-2">Maintenance Reserve (Annual)</label>
                    <input
                      type="number"
                      name="maintenanceReserve"
                      value={expenses.operatingExpenses.maintenanceReserve}
                      onChange={handleExpenseChange}
                      min="0"
                      step="10"
                      className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  {/* Utilities */}
                  <div>
                    <label className="block text-gray-700 font-medium mb-2">Utilities (Annual)</label>
                    <input
                      type="number"
                      name="utilities"
                      value={expenses.operatingExpenses.utilities}
                      onChange={handleExpenseChange}
                      min="0"
                      step="10"
                      className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  {/* Other Expenses */}
                  <div>
                    <label className="block text-gray-700 font-medium mb-2">Other Expenses (Annual)</label>
                    <input
                      type="number"
                      name="other"
                      value={expenses.operatingExpenses.other}
                      onChange={handleExpenseChange}
                      min="0"
                      step="10"
                      className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>
              
              <div className="mb-8">
                <h2 className="text-xl font-semibold mb-4">Vacancy Rate</h2>
                
                <div className="max-w-md">
                  <label className="block text-gray-700 font-medium mb-2">
                    Expected Vacancy Rate (%)
                  </label>
                  <input
                    type="number"
                    name="vacancyRate"
                    value={expenses.vacancyRate}
                    onChange={handleVacancyRateChange}
                    min="0"
                    max="100"
                    step="0.5"
                    className={`w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                      errors.vacancyRate ? 'border-red-500' : 'border-gray-300'
                    }`}
                  />
                  {errors.vacancyRate && (
                    <p className="mt-1 text-red-500 text-sm">{errors.vacancyRate}</p>
                  )}
                  <p className="mt-2 text-sm text-gray-600">
                    This rate represents the percentage of time the property is expected to be vacant over the course of a year.
                  </p>
                </div>
              </div>
              
              <div className="mb-8">
                <h2 className="text-xl font-semibold mb-4">Expense Summary</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <MetricCard
                    label="Total Annual Expenses"
                    value={formatCurrency(expenses.totalAnnualExpenses)}
                    description="All operating expenses combined"
                  />
                  
                  <MetricCard
                    label="Monthly Expenses"
                    value={formatCurrency(expenses.totalMonthlyExpenses)}
                    description="Average monthly operational cost"
                  />
                  
                  <MetricCard
                    label="Expense Ratio"
                    value={formatPercent(expenses.totalAnnualExpenses / (property.purchasePrice || 1))}
                    description="Expenses as % of property value"
                  />
                </div>
                
                <div className="mt-6">
                  <InfoBox variant="info" title="About Operating Expenses">
                    <p>Operating expenses are the ongoing costs associated with maintaining and managing your investment property. 
                    These typically do not include mortgage payments or depreciation.</p>
                    <p className="mt-2">A good rule of thumb is to budget around 1-4% of the property value for annual maintenance, 
                    depending on the age and condition of the property.</p>
                  </InfoBox>
                </div>
              </div>
            </div>
          )}
          
          {/* Tax Benefits Tab */}
          {activeTab === 'tax' && (
            <div>
              <div className="mb-8">
                <h2 className="text-xl font-semibold mb-4">Tax Information</h2>
                
                <div className="max-w-md mb-6">
                  <label className="block text-gray-700 font-medium mb-2">
                    Your Marginal Tax Rate (%)
                  </label>
                  <input
                    type="number"
                    name="taxRate"
                    value={taxBenefits.taxRate}
                    onChange={handleTaxRateChange}
                    min="0"
                    max="100"
                    step="0.5"
                    className={`w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                      errors.taxRate ? 'border-red-500' : 'border-gray-300'
                    }`}
                  />
                  {errors.taxRate && (
                    <p className="mt-1 text-red-500 text-sm">{errors.taxRate}</p>
                  )}
                  <p className="mt-2 text-sm text-gray-600">
                    This is your highest income tax bracket rate. In Germany, this is typically between 14% and 45%.
                  </p>
                </div>
              </div>
              
              <div className="mb-8">
                <h2 className="text-xl font-semibold mb-4">Depreciation</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Building Value */}
                  <div>
                    <label className="block text-gray-700 font-medium mb-2">Building Value</label>
                    <input
                      type="number"
                      name="buildingValue"
                      value={taxBenefits.depreciation.buildingValue}
                      onChange={handleDepreciationChange}
                      min="0"
                      step="1000"
                      className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <p className="mt-1 text-sm text-gray-600">
                      This is the portion of the purchase price attributed to the building (excluding land).
                    </p>
                  </div>
                  
                  {/* Building Percentage */}
                  <div>
                    <label className="block text-gray-700 font-medium mb-2">Building Percentage (%)</label>
                    <input
                      type="number"
                      name="buildingPercentage"
                      value={taxBenefits.depreciation.buildingPercentage}
                      onChange={handleDepreciationChange}
                      min="0"
                      max="100"
                      step="1"
                      className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <p className="mt-1 text-sm text-gray-600">
                      Percentage of property value that is attributed to the building (usually 70-90%).
                    </p>
                  </div>
                  
                  {/* Depreciation Period */}
                  <div>
                    <label className="block text-gray-700 font-medium mb-2">Depreciation Period (years)</label>
                    <input
                      type="number"
                      name="depreciationPeriod"
                      value={taxBenefits.depreciation.depreciationPeriod}
                      onChange={handleDepreciationChange}
                      min="1"
                      step="1"
                      className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <p className="mt-1 text-sm text-gray-600">
                      In Germany, residential buildings are typically depreciated over 50 years (2% per year).
                    </p>
                  </div>
                  
                  {/* Annual Depreciation */}
                  <div>
                    <label className="block text-gray-700 font-medium mb-2">Annual Depreciation Amount</label>
                    <input
                      type="text"
                      value={formatCurrency(taxBenefits.depreciation.annualDepreciation)}
                      className="w-full p-3 border border-gray-300 rounded-lg bg-gray-50"
                      disabled
                    />
                    <p className="mt-1 text-sm text-gray-600">
                      This is the amount you can deduct each year for building depreciation.
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="mb-8">
                <h2 className="text-xl font-semibold mb-4">Tax Benefit Summary</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <MetricCard
                    label="Annual Deductible Expenses"
                    value={formatCurrency(expenses.totalAnnualExpenses)}
                    description="Operating expenses you can deduct"
                  />
                  
                  <MetricCard
                    label="Annual Interest Payments"
                    value={formatCurrency(taxBenefits.interestPayments)}
                    description="Mortgage interest (tax deductible)"
                  />
                  
                  <MetricCard
                    label="Annual Depreciation"
                    value={formatCurrency(taxBenefits.depreciation.annualDepreciation)}
                    description="Building depreciation deduction"
                  />
                  
                  <MetricCard
                    label="Total Tax Deductions"
                    value={formatCurrency(taxBenefits.totalTaxDeductions)}
                    description="All tax deductible expenses"
                    variant="success"
                  />
                  
                  <MetricCard
                    label="Annual Tax Savings"
                    value={formatCurrency(taxBenefits.taxSavings)}
                    description={`Based on ${taxBenefits.taxRate}% tax rate`}
                    variant="success"
                  />
                  
                  <MetricCard
                    label="Monthly Tax Savings"
                    value={formatCurrency(taxBenefits.monthlyTaxSavings)}
                    description="Average monthly tax benefit"
                    variant="success"
                  />
                </div>
                
                <div className="mt-6">
                  <InfoBox variant="info" title="About Tax Benefits">
                    <p>In Germany, rental property investors can deduct various expenses from their rental income, 
                    including mortgage interest, operating expenses, and building depreciation.</p>
                    <p className="mt-2">These deductions reduce your taxable income, resulting in tax savings based on your personal tax rate.</p>
                    <p className="mt-2">Note: This is a simplified calculation. Please consult with a tax professional for advice specific to your situation.</p>
                  </InfoBox>
                </div>
              </div>
            </div>
          )}
          
          {/* Form Actions */}
          <div className="mt-8 flex justify-between">
            <button
              type="button"
              onClick={handleBack}
              className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Back: Financing
            </button>
            
            <button
              type="submit"
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Next: Analysis Results
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ExpensesTaxPage;