import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProperty } from '../contexts/PropertyContext';
import { useFinancing } from '../contexts/FinancingContext';
import { formatCurrency } from '../utils/formatters';
import InfoBox from '../components/common/InfoBox';
import MetricCard from '../components/common/MetricCard';

const FinancingPage = () => {
  const navigate = useNavigate();
  const { property } = useProperty();
  const { financing, updateFinancing, isLoading } = useFinancing();
  const [errors, setErrors] = useState({});

  // Check if property data exists, redirect if not
  useEffect(() => {
    if (!property.address) {
      navigate('/property-input');
    }
  }, [property, navigate]);

  // Handle form field changes
  const handleInputChange = (e) => {
    const { name, value, type } = e.target;
    
    // Convert numeric inputs to numbers
    if (type === 'number') {
      updateFinancing({ [name]: parseFloat(value) || 0 });
    } else {
      updateFinancing({ [name]: value });
    }
  };

  // Calculate loan amount when down payment percentage changes
  const handleDownPaymentPercentChange = (e) => {
    const downPaymentPercentage = parseFloat(e.target.value) || 0;
    const downPaymentAmount = (property.purchasePrice * downPaymentPercentage) / 100;
    
    updateFinancing({
      downPaymentPercentage,
      downPaymentAmount,
      loanAmount: property.purchasePrice - downPaymentAmount
    });
  };

  // Calculate down payment percentage when amount changes
  const handleDownPaymentAmountChange = (e) => {
    const downPaymentAmount = parseFloat(e.target.value) || 0;
    const downPaymentPercentage = (downPaymentAmount / property.purchasePrice) * 100;
    
    updateFinancing({
      downPaymentAmount,
      downPaymentPercentage,
      loanAmount: property.purchasePrice - downPaymentAmount
    });
  };

  // Validate the form before submission
  const validateForm = () => {
    const newErrors = {};
    
    if (financing.downPaymentPercentage <= 0) {
      newErrors.downPaymentPercentage = 'Down payment percentage must be greater than 0';
    }
    
    if (financing.interestRate <= 0) {
      newErrors.interestRate = 'Interest rate must be greater than 0';
    }
    
    if (financing.loanTerm <= 0) {
      newErrors.loanTerm = 'Loan term must be greater than 0';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (validateForm()) {
      navigate('/expenses-tax');
    }
  };

  // Navigate back to previous step
  const handleBack = () => {
    navigate('/rental-units');
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Financing</h1>
      
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <form onSubmit={handleSubmit}>
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">Mortgage Details</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Purchase Price (read-only) */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">Purchase Price</label>
                <input
                  type="text"
                  value={formatCurrency(property.purchasePrice)}
                  className="w-full p-3 border border-gray-300 rounded-lg bg-gray-50"
                  disabled
                />
              </div>
              
              {/* Down Payment Percentage */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">Down Payment (%)</label>
                <input
                  type="number"
                  name="downPaymentPercentage"
                  value={financing.downPaymentPercentage}
                  onChange={handleDownPaymentPercentChange}
                  min="0"
                  max="100"
                  step="0.5"
                  className={`w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    errors.downPaymentPercentage ? 'border-red-500' : 'border-gray-300'
                  }`}
                  required
                />
                {errors.downPaymentPercentage && (
                  <p className="mt-1 text-red-500 text-sm">{errors.downPaymentPercentage}</p>
                )}
              </div>
              
              {/* Down Payment Amount */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">Down Payment Amount</label>
                <input
                  type="number"
                  name="downPaymentAmount"
                  value={financing.downPaymentAmount}
                  onChange={handleDownPaymentAmountChange}
                  min="0"
                  step="1000"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              {/* Loan Amount */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">Loan Amount</label>
                <input
                  type="number"
                  name="loanAmount"
                  value={financing.loanAmount}
                  onChange={handleInputChange}
                  min="0"
                  step="1000"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              {/* Interest Rate */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">Interest Rate (%)</label>
                <input
                  type="number"
                  name="interestRate"
                  value={financing.interestRate}
                  onChange={handleInputChange}
                  min="0"
                  max="20"
                  step="0.1"
                  className={`w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    errors.interestRate ? 'border-red-500' : 'border-gray-300'
                  }`}
                  required
                />
                {errors.interestRate && (
                  <p className="mt-1 text-red-500 text-sm">{errors.interestRate}</p>
                )}
              </div>
              
              {/* Repayment Rate */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">Repayment Rate (%)</label>
                <input
                  type="number"
                  name="repaymentRate"
                  value={financing.repaymentRate}
                  onChange={handleInputChange}
                  min="0"
                  max="20"
                  step="0.1"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              {/* Loan Term */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">Loan Term (years)</label>
                <input
                  type="number"
                  name="loanTerm"
                  value={financing.loanTerm}
                  onChange={handleInputChange}
                  min="1"
                  max="40"
                  step="1"
                  className={`w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    errors.loanTerm ? 'border-red-500' : 'border-gray-300'
                  }`}
                  required
                />
                {errors.loanTerm && (
                  <p className="mt-1 text-red-500 text-sm">{errors.loanTerm}</p>
                )}
              </div>
              
              {/* Monthly Payment */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">Monthly Payment</label>
                <input
                  type="text"
                  value={formatCurrency(financing.monthlyPayment)}
                  className="w-full p-3 border border-gray-300 rounded-lg bg-gray-50"
                  disabled
                />
              </div>
            </div>
          </div>
          
          {/* Closing Costs Section */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">Closing Costs</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <MetricCard
                label="Property Transfer Tax"
                value={formatCurrency(financing.closingCosts.transferTax)}
                description={`Based on ${property.region || 'Default'} tax rate`}
              />
              
              <MetricCard
                label="Notary Fee"
                value={formatCurrency(financing.closingCosts.notaryFee)}
                description="Legal documentation fees"
              />
              
              <MetricCard
                label="Land Registry"
                value={formatCurrency(financing.closingCosts.landRegistry)}
                description="Registration fees"
              />
              
              <MetricCard
                label="Real Estate Agent Fee"
                value={formatCurrency(financing.closingCosts.agentFee)}
                description="Typically 3.57% incl. VAT"
              />
              
              <MetricCard
                label="Total Closing Costs"
                value={formatCurrency(financing.closingCosts.totalClosingCosts)}
                description="All one-time transaction costs"
                variant="warning"
              />
              
              <MetricCard
                label="Total Acquisition Cost"
                value={formatCurrency(financing.totalAcquisitionCost)}
                description="Purchase price + closing costs"
                variant="warning"
              />
            </div>
            
            <div className="mt-6">
              <InfoBox variant="info" title="About Closing Costs">
                <p>Closing costs are the one-time expenses associated with the property purchase transaction. 
                These typically include property transfer tax, notary fees, land registry fees, and real estate agent fees.</p>
                <p className="mt-2">These costs are calculated based on the purchase price and the region/state where the property is located.</p>
              </InfoBox>
            </div>
          </div>
          
          {/* Form Actions */}
          <div className="mt-8 flex justify-between">
            <button
              type="button"
              onClick={handleBack}
              className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Back: Rental Units
            </button>
            
            <button
              type="submit"
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            >
              Next: Expenses & Tax
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default FinancingPage;