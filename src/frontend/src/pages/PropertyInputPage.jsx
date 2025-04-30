import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProperty } from '../contexts/PropertyContext';
import apiService from '../services/api';
import { formatCurrency } from '../utils/formatters';

const PropertyInputPage = () => {
  const navigate = useNavigate();
  const { property, updateProperty, marketData, setMarketData, setMarketDataTaskId, isLoading, setIsLoading } = useProperty();
  const [error, setError] = useState(null);

  // Property types options
  const propertyTypes = [
    { value: 'apartment', label: 'Apartment' },
    { value: 'house', label: 'House' },
    { value: 'multi-family', label: 'Multi-family Home' },
    { value: 'commercial', label: 'Commercial Property' }
  ];

  // Condition options
  const conditionOptions = [
    { value: 'excellent', label: 'Excellent' },
    { value: 'good', label: 'Good' },
    { value: 'average', label: 'Average' },
    { value: 'needs-work', label: 'Needs Work' },
    { value: 'fixer-upper', label: 'Fixer Upper' }
  ];

  // Handle form field changes
  const handleChange = (e) => {
    const { name, value, type } = e.target;
    
    // Convert numeric inputs to numbers
    if (type === 'number') {
      updateProperty({ [name]: parseFloat(value) || 0 });
    } else {
      updateProperty({ [name]: value });
    }
  };

  // Fetch market data for the property
  const fetchMarketData = async () => {
    if (!property.location || !property.propertyType) {
      setError('Please provide a location and property type');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiService.fetchMarketData(
        property.location,
        property.propertyType
      );
      
      if (response.task_id) {
        setMarketDataTaskId(response.task_id);
        checkTaskStatus(response.task_id);
      } else {
        setMarketData(response);
        setIsLoading(false);
      }
    } catch (error) {
      console.error('Error fetching market data:', error);
      setError('Failed to fetch market data. Please try again.');
      setIsLoading(false);
    }
  };

  // Check task status for market data
  const checkTaskStatus = async (taskId) => {
    try {
      const response = await apiService.getTaskResult(taskId);
      
      if (response.status === 'completed') {
        setMarketData(response.result);
        setIsLoading(false);
      } else if (response.status === 'failed') {
        setError('Market data analysis failed. Please try again.');
        setIsLoading(false);
      } else {
        // Task is still running, check again in 2 seconds
        setTimeout(() => checkTaskStatus(taskId), 2000);
      }
    } catch (error) {
      console.error('Error checking task status:', error);
      setError('Failed to get market data. Please try again.');
      setIsLoading(false);
    }
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    navigate('/rental-units');
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Property Information</h1>
      
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Address */}
            <div className="md:col-span-2">
              <label className="block text-gray-700 font-medium mb-2">Property Address</label>
              <input
                type="text"
                name="address"
                value={property.address}
                onChange={handleChange}
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter the property address"
                required
              />
            </div>
            
            {/* Location */}
            <div>
              <label className="block text-gray-700 font-medium mb-2">Location/Neighborhood</label>
              <input
                type="text"
                name="location"
                value={property.location}
                onChange={handleChange}
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter the location or neighborhood"
                required
              />
            </div>
            
            {/* Region */}
            <div>
              <label className="block text-gray-700 font-medium mb-2">Region/State</label>
              <input
                type="text"
                name="region"
                value={property.region}
                onChange={handleChange}
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Berlin, Hamburg, etc."
                required
              />
            </div>
            
            {/* Property Type */}
            <div>
              <label className="block text-gray-700 font-medium mb-2">Property Type</label>
              <select
                name="propertyType"
                value={property.propertyType}
                onChange={handleChange}
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                {propertyTypes.map(type => (
                  <option key={type.value} value={type.value}>{type.label}</option>
                ))}
              </select>
            </div>
            
            {/* Purchase Price */}
            <div>
              <label className="block text-gray-700 font-medium mb-2">Purchase Price (€)</label>
              <input
                type="number"
                name="purchasePrice"
                value={property.purchasePrice}
                onChange={handleChange}
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="0"
                min="0"
                step="1000"
                required
              />
            </div>
            
            {/* Property Size */}
            <div>
              <label className="block text-gray-700 font-medium mb-2">Size (m²)</label>
              <input
                type="number"
                name="sizeSqm"
                value={property.sizeSqm}
                onChange={handleChange}
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="0"
                min="0"
                required
              />
            </div>
            
            {/* Number of Units */}
            <div>
              <label className="block text-gray-700 font-medium mb-2">Number of Units</label>
              <input
                type="number"
                name="numUnits"
                value={property.numUnits}
                onChange={handleChange}
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="1"
                min="1"
                required
              />
            </div>
            
            {/* Year Built */}
            <div>
              <label className="block text-gray-700 font-medium mb-2">Year Built</label>
              <input
                type="number"
                name="yearBuilt"
                value={property.yearBuilt}
                onChange={handleChange}
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="2000"
                min="1800"
                max={new Date().getFullYear()}
                required
              />
            </div>
            
            {/* Condition */}
            <div>
              <label className="block text-gray-700 font-medium mb-2">Property Condition</label>
              <select
                name="condition"
                value={property.condition}
                onChange={handleChange}
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                {conditionOptions.map(option => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </div>
          </div>
          
          {/* Market Data Section */}
          <div className="mt-8">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Market Data</h2>
              <button
                type="button"
                onClick={fetchMarketData}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                disabled={isLoading}
              >
                {isLoading ? 'Analyzing...' : 'Get Market Data'}
              </button>
            </div>
            
            {error && (
              <div className="mb-4 p-3 bg-red-100 text-red-800 rounded-lg">
                {error}
              </div>
            )}
            
            {isLoading && (
              <div className="mb-4 p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mr-3"></div>
                  <p>Analyzing market data for this property...</p>
                </div>
              </div>
            )}
            
            {marketData && (
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h3 className="text-sm font-medium text-gray-500">Estimated Market Value</h3>
                    <p className="text-xl font-bold text-gray-800">{formatCurrency(marketData.estimated_value)}</p>
                    <p className="text-xs text-gray-500">Range: {formatCurrency(marketData.value_range?.min)} - {formatCurrency(marketData.value_range?.max)}</p>
                  </div>
                  
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h3 className="text-sm font-medium text-gray-500">Avg. Price per m²</h3>
                    <p className="text-xl font-bold text-gray-800">{formatCurrency(marketData.price_per_sqm)}</p>
                    <p className="text-xs text-gray-500">Area average</p>
                  </div>
                  
                  <div className="bg-white p-4 rounded-lg shadow-sm">
                    <h3 className="text-sm font-medium text-gray-500">Potential Monthly Rent</h3>
                    <p className="text-xl font-bold text-gray-800">{formatCurrency(marketData.potential_rent?.monthly)}</p>
                    <p className="text-xs text-gray-500">Based on market analysis</p>
                  </div>
                </div>
                
                {marketData.market_trends && (
                  <div className="mt-4">
                    <h3 className="font-medium mb-2">Market Trends</h3>
                    <p className="text-sm text-gray-700">{marketData.market_trends.summary}</p>
                    
                    <div className="mt-2 flex">
                      <div className="mr-4">
                        <span className="text-xs text-gray-500">Annual Appreciation:</span>
                        <span className="ml-1 text-sm font-medium">{marketData.market_trends.annual_appreciation}%</span>
                      </div>
                      <div>
                        <span className="text-xs text-gray-500">Rent Growth:</span>
                        <span className="ml-1 text-sm font-medium">{marketData.market_trends.rent_growth}%</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
          
          {/* Form Actions */}
          <div className="mt-8 flex justify-end">
            <button
              type="submit"
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Next: Rental Units
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PropertyInputPage;