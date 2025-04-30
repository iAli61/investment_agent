import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProperty } from '../contexts/PropertyContext';
import { useUnits } from '../contexts/UnitsContext';
import { formatCurrency, formatArea } from '../utils/formatters';
import apiService from '../services/api';

const RentalUnitsPage = () => {
  const navigate = useNavigate();
  const { property } = useProperty();
  const { 
    units, 
    addUnit, 
    updateUnit, 
    removeUnit, 
    getTotals, 
    rentEstimates, 
    setRentEstimates,
    isLoading, 
    setIsLoading 
  } = useUnits();
  
  const [newUnit, setNewUnit] = useState({
    unitNumber: '',
    type: 'apartment',
    bedrooms: 1,
    bathrooms: 1,
    sizeSqm: 0,
    isRented: false,
    monthlyRent: 0,
    features: []
  });
  
  const [errorMessage, setErrorMessage] = useState('');
  const [activeTab, setActiveTab] = useState('units');

  // Check if property data exists, redirect if not
  useEffect(() => {
    if (!property.address) {
      navigate('/property-input');
    }
  }, [property, navigate]);

  // Handle input change for new unit form
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    if (type === 'checkbox') {
      setNewUnit({ ...newUnit, [name]: checked });
    } else if (type === 'number') {
      setNewUnit({ ...newUnit, [name]: parseFloat(value) || 0 });
    } else {
      setNewUnit({ ...newUnit, [name]: value });
    }
  };

  // Handle feature selection
  const handleFeatureToggle = (feature) => {
    const features = [...newUnit.features];
    
    if (features.includes(feature)) {
      const index = features.indexOf(feature);
      features.splice(index, 1);
    } else {
      features.push(feature);
    }
    
    setNewUnit({ ...newUnit, features });
  };

  // Handle form submission to add a new unit
  const handleAddUnit = (e) => {
    e.preventDefault();
    
    if (!newUnit.unitNumber) {
      setErrorMessage('Please provide a unit number/name');
      return;
    }
    
    // Add the new unit
    addUnit({
      ...newUnit,
      propertyType: property.propertyType
    });
    
    // Reset the form
    setNewUnit({
      unitNumber: '',
      type: 'apartment',
      bedrooms: 1,
      bathrooms: 1,
      sizeSqm: 0,
      isRented: false,
      monthlyRent: 0,
      features: []
    });
    
    setErrorMessage('');
  };

  // Request rent estimation from API
  const handleRentEstimation = async () => {
    // Validate minimum data needed for estimation
    if (!property.location || !property.propertyType) {
      setErrorMessage('Property location and type are required for rent estimation');
      return;
    }
    
    if (!newUnit.sizeSqm) {
      setErrorMessage('Unit size is required for rent estimation');
      return;
    }
    
    setIsLoading(true);
    setErrorMessage('');
    
    try {
      const response = await apiService.estimateRent({
        location: property.location,
        property_type: property.propertyType,
        size_sqm: newUnit.sizeSqm,
        bedrooms: newUnit.bedrooms,
        bathrooms: newUnit.bathrooms,
        features: newUnit.features,
        condition: property.condition
      });
      
      if (response.estimated_rent) {
        // Update rent estimates with new data
        setRentEstimates([
          ...rentEstimates,
          {
            id: Date.now().toString(),
            unit: { ...newUnit },
            estimate: response
          }
        ]);
        
        // Update the new unit form with the estimated rent
        setNewUnit({
          ...newUnit,
          monthlyRent: response.estimated_rent
        });
      }
      
      setIsLoading(false);
    } catch (error) {
      console.error('Error estimating rent:', error);
      setErrorMessage('Failed to estimate rent. Please try again.');
      setIsLoading(false);
    }
  };

  // Handle unit deletion
  const handleDeleteUnit = (unitId) => {
    if (window.confirm('Are you sure you want to delete this unit?')) {
      removeUnit(unitId);
    }
  };

  // Navigate to next section
  const handleContinue = () => {
    navigate('/financing');
  };

  // Available property features
  const availableFeatures = [
    { id: 'balcony', label: 'Balcony' },
    { id: 'garden', label: 'Garden' },
    { id: 'parking', label: 'Parking' },
    { id: 'elevator', label: 'Elevator' },
    { id: 'furnished', label: 'Furnished' },
    { id: 'modernKitchen', label: 'Modern Kitchen' },
    { id: 'floorHeating', label: 'Floor Heating' },
    { id: 'airConditioning', label: 'Air Conditioning' }
  ];

  // Get unit totals
  const totals = getTotals();

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Rental Units</h1>
      
      {/* Tabs */}
      <div className="mb-6 border-b border-gray-200">
        <nav className="flex -mb-px">
          <button
            onClick={() => setActiveTab('units')}
            className={`${
              activeTab === 'units'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm`}
          >
            Units Management
          </button>
          <button
            onClick={() => setActiveTab('rent')}
            className={`${
              activeTab === 'rent'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm`}
          >
            Rent Estimations
          </button>
        </nav>
      </div>
      
      {/* Units Management Tab */}
      {activeTab === 'units' && (
        <div>
          {/* Current Units */}
          {units.length > 0 && (
            <div className="mb-8">
              <h2 className="text-xl font-semibold mb-4">Current Units</h2>
              <div className="bg-white rounded-lg shadow overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Unit</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Details</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rent</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {units.map((unit) => (
                      <tr key={unit.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{unit.unitNumber}</div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-900">{unit.bedrooms} bed, {unit.bathrooms} bath</div>
                          <div className="text-sm text-gray-500">{formatArea(unit.sizeSqm)}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{formatCurrency(unit.monthlyRent)}/month</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            unit.isRented ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                          }`}>
                            {unit.isRented ? 'Occupied' : 'Vacant'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button 
                            className="text-blue-600 hover:text-blue-900 mr-4"
                            onClick={() => {/* Edit unit functionality */}}
                          >
                            Edit
                          </button>
                          <button 
                            className="text-red-600 hover:text-red-900"
                            onClick={() => handleDeleteUnit(unit.id)}
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot className="bg-gray-50">
                    <tr>
                      <td className="px-6 py-3 text-sm font-semibold">Total: {totals.totalUnits} units</td>
                      <td className="px-6 py-3 text-sm">
                        <div>Total: {totals.totalBedrooms} bedrooms, {totals.totalBathrooms} bathrooms</div>
                        <div>{formatArea(totals.totalSizeSqm)}</div>
                      </td>
                      <td className="px-6 py-3 text-sm font-semibold">
                        {formatCurrency(totals.totalMonthlyRent)}/month
                      </td>
                      <td className="px-6 py-3 text-sm">
                        {totals.rentedUnits} of {totals.totalUnits} occupied
                      </td>
                      <td></td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>
          )}

          {/* Add New Unit Form */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Add New Unit</h2>
            
            {errorMessage && (
              <div className="mb-4 p-3 bg-red-100 text-red-800 rounded-lg">
                {errorMessage}
              </div>
            )}
            
            <form onSubmit={handleAddUnit}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Unit Number */}
                <div>
                  <label className="block text-gray-700 font-medium mb-2">Unit Number/Name</label>
                  <input
                    type="text"
                    name="unitNumber"
                    value={newUnit.unitNumber}
                    onChange={handleInputChange}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Apartment 1A, Unit 3, etc."
                  />
                </div>
                
                {/* Unit Type */}
                <div>
                  <label className="block text-gray-700 font-medium mb-2">Unit Type</label>
                  <select
                    name="type"
                    value={newUnit.type}
                    onChange={handleInputChange}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="apartment">Apartment</option>
                    <option value="studio">Studio</option>
                    <option value="house">House</option>
                    <option value="commercial">Commercial</option>
                  </select>
                </div>
                
                {/* Bedrooms */}
                <div>
                  <label className="block text-gray-700 font-medium mb-2">Bedrooms</label>
                  <input
                    type="number"
                    name="bedrooms"
                    value={newUnit.bedrooms}
                    onChange={handleInputChange}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="0"
                    step="1"
                  />
                </div>
                
                {/* Bathrooms */}
                <div>
                  <label className="block text-gray-700 font-medium mb-2">Bathrooms</label>
                  <input
                    type="number"
                    name="bathrooms"
                    value={newUnit.bathrooms}
                    onChange={handleInputChange}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="0"
                    step="0.5"
                  />
                </div>
                
                {/* Size */}
                <div>
                  <label className="block text-gray-700 font-medium mb-2">Size (m²)</label>
                  <input
                    type="number"
                    name="sizeSqm"
                    value={newUnit.sizeSqm}
                    onChange={handleInputChange}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="0"
                    step="1"
                  />
                </div>
                
                {/* Monthly Rent */}
                <div>
                  <div className="flex justify-between">
                    <label className="block text-gray-700 font-medium mb-2">Monthly Rent (€)</label>
                    <button
                      type="button"
                      onClick={handleRentEstimation}
                      className="text-sm text-blue-600 hover:text-blue-800"
                      disabled={isLoading}
                    >
                      {isLoading ? 'Estimating...' : 'Estimate Rent'}
                    </button>
                  </div>
                  <input
                    type="number"
                    name="monthlyRent"
                    value={newUnit.monthlyRent}
                    onChange={handleInputChange}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="0"
                    step="10"
                  />
                </div>
                
                {/* Occupied Status */}
                <div className="flex items-center h-full pt-8">
                  <input
                    type="checkbox"
                    id="isRented"
                    name="isRented"
                    checked={newUnit.isRented}
                    onChange={handleInputChange}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="isRented" className="ml-2 block text-gray-700">
                    Unit is currently occupied
                  </label>
                </div>
              </div>
              
              {/* Features */}
              <div className="mt-6">
                <label className="block text-gray-700 font-medium mb-2">Features</label>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                  {availableFeatures.map((feature) => (
                    <div key={feature.id} className="flex items-center">
                      <input
                        type="checkbox"
                        id={feature.id}
                        checked={newUnit.features.includes(feature.id)}
                        onChange={() => handleFeatureToggle(feature.id)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <label htmlFor={feature.id} className="ml-2 block text-gray-700 text-sm">
                        {feature.label}
                      </label>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Form Actions */}
              <div className="mt-8 flex justify-end">
                <button
                  type="submit"
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  Add Unit
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      {/* Rent Estimations Tab */}
      {activeTab === 'rent' && (
        <div>
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Rent Estimations</h2>
            
            {rentEstimates.length === 0 ? (
              <p className="text-gray-600">No rent estimations yet. Use the "Estimate Rent" button when adding a unit to get AI-powered rent estimates.</p>
            ) : (
              <div className="space-y-6">
                {rentEstimates.map((item) => (
                  <div key={item.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <h3 className="text-lg font-medium text-gray-900">
                        {item.unit.unitNumber || 'Unit'} - {item.unit.bedrooms} bed, {item.unit.bathrooms} bath
                      </h3>
                      <span className="text-xl font-bold text-blue-600">
                        {formatCurrency(item.estimate.estimated_rent)}/month
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                      <div className="bg-gray-50 p-3 rounded">
                        <h4 className="text-sm font-medium text-gray-500">Rent Range</h4>
                        <div className="text-sm mt-1">
                          <span className="text-gray-600">Low: </span>
                          <span className="font-medium">{formatCurrency(item.estimate.rent_range?.low || 0)}</span>
                        </div>
                        <div className="text-sm">
                          <span className="text-gray-600">High: </span>
                          <span className="font-medium">{formatCurrency(item.estimate.rent_range?.high || 0)}</span>
                        </div>
                        <div className="text-sm">
                          <span className="text-gray-600">Per m²: </span>
                          <span className="font-medium">
                            {formatCurrency(item.estimate.rent_per_sqm || 0, '€')}/m²
                          </span>
                        </div>
                      </div>
                      
                      <div className="bg-gray-50 p-3 rounded">
                        <h4 className="text-sm font-medium text-gray-500">Property Details</h4>
                        <div className="text-sm mt-1">
                          <span className="text-gray-600">Size: </span>
                          <span className="font-medium">{formatArea(item.unit.sizeSqm)}</span>
                        </div>
                        <div className="text-sm">
                          <span className="text-gray-600">Location: </span>
                          <span className="font-medium">{property.location}</span>
                        </div>
                        <div className="text-sm">
                          <span className="text-gray-600">Type: </span>
                          <span className="font-medium">{item.unit.type}</span>
                        </div>
                      </div>
                      
                      <div className="bg-gray-50 p-3 rounded">
                        <h4 className="text-sm font-medium text-gray-500">Confidence</h4>
                        <div className="text-sm mt-1">
                          <span className="text-gray-600">Level: </span>
                          <span className="font-medium">
                            {(item.estimate.confidence_level * 100).toFixed(0)}%
                          </span>
                        </div>
                        <div className="text-sm">
                          <span className="text-gray-600">Source Count: </span>
                          <span className="font-medium">
                            {item.estimate.sources?.length || 0}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    {item.estimate.explanation && (
                      <div className="mt-4">
                        <h4 className="text-sm font-medium text-gray-500">Explanation</h4>
                        <p className="text-sm text-gray-700 mt-1">{item.estimate.explanation}</p>
                      </div>
                    )}
                    
                    {item.estimate.legal_limit_warning && (
                      <div className="mt-4 p-3 bg-yellow-50 border-l-4 border-yellow-400 text-sm text-yellow-800">
                        <div className="font-medium">Rent Cap Warning</div>
                        <p>The estimated rent exceeds the legal limit in this area. Maximum allowed: {formatCurrency(item.estimate.legal_limit)}</p>
                      </div>
                    )}
                    
                    <div className="mt-4 flex justify-end">
                      <button
                        className="text-blue-600 hover:text-blue-800 text-sm"
                        onClick={() => {
                          // Find the unit and update its rent
                          const unitIndex = units.findIndex(u => u.unitNumber === item.unit.unitNumber);
                          if (unitIndex !== -1) {
                            updateUnit(units[unitIndex].id, { 
                              monthlyRent: item.estimate.estimated_rent 
                            });
                          }
                        }}
                      >
                        Apply This Estimate
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Navigation Buttons */}
      <div className="mt-8 flex justify-between">
        <button
          type="button"
          onClick={() => navigate('/property-input')}
          className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Back: Property Details
        </button>
        
        <button
          type="button"
          onClick={handleContinue}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={units.length === 0}
        >
          Next: Financing
        </button>
      </div>
    </div>
  );
};

export default RentalUnitsPage;