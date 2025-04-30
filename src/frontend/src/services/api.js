/**
 * Service for API communication
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

/**
 * Make an API request with error handling
 * @param {string} endpoint - API endpoint
 * @param {Object} options - Fetch options
 * @returns {Promise} Response data
 */
const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `API error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

/**
 * API services for property investment analysis
 */
const apiService = {
  /**
   * Fetch market data for a property
   * @param {string} location - Property location
   * @param {string} propertyType - Type of property
   * @returns {Promise} Market data or task ID
   */
  fetchMarketData: (location, propertyType) => {
    return apiRequest('/market-data', {
      method: 'POST',
      body: JSON.stringify({ location, property_type: propertyType })
    });
  },
  
  /**
   * Estimate rent for a property
   * @param {Object} propertyData - Property details
   * @returns {Promise} Rent estimate or task ID
   */
  estimateRent: (propertyData) => {
    return apiRequest('/rent-estimate', {
      method: 'POST',
      body: JSON.stringify(propertyData)
    });
  },
  
  /**
   * Run a comprehensive investment analysis
   * @param {Object} analysisData - Complete property investment data
   * @returns {Promise} Analysis results or task ID
   */
  runInvestmentAnalysis: (analysisData) => {
    return apiRequest('/investment-analysis', {
      method: 'POST',
      body: JSON.stringify(analysisData)
    });
  },
  
  /**
   * Get risk assessment for an investment
   * @param {Object} investmentData - Investment details
   * @returns {Promise} Risk assessment data or task ID
   */
  getRiskAssessment: (investmentData) => {
    return apiRequest('/risk-assessment', {
      method: 'POST',
      body: JSON.stringify(investmentData)
    });
  },
  
  /**
   * Save an investment scenario
   * @param {Object} scenarioData - Complete scenario data
   * @returns {Promise} Saved scenario with ID
   */
  saveScenario: (scenarioData) => {
    return apiRequest('/scenarios', {
      method: 'POST',
      body: JSON.stringify(scenarioData)
    });
  },
  
  /**
   * Get all saved scenarios
   * @returns {Promise} List of scenarios
   */
  getScenarios: () => {
    return apiRequest('/scenarios');
  },
  
  /**
   * Get a specific scenario by ID
   * @param {string} scenarioId - Scenario ID
   * @returns {Promise} Scenario data
   */
  getScenarioById: (scenarioId) => {
    return apiRequest(`/scenarios/${scenarioId}`);
  },
  
  /**
   * Update an existing scenario
   * @param {string} scenarioId - Scenario ID
   * @param {Object} scenarioData - Updated scenario data
   * @returns {Promise} Updated scenario
   */
  updateScenario: (scenarioId, scenarioData) => {
    return apiRequest(`/scenarios/${scenarioId}`, {
      method: 'PUT',
      body: JSON.stringify(scenarioData)
    });
  },
  
  /**
   * Delete a scenario
   * @param {string} scenarioId - Scenario ID
   * @returns {Promise} Success message
   */
  deleteScenario: (scenarioId) => {
    return apiRequest(`/scenarios/${scenarioId}`, {
      method: 'DELETE'
    });
  },
  
  /**
   * Compare multiple scenarios
   * @param {Array} scenarioIds - Array of scenario IDs to compare
   * @returns {Promise} Comparison data
   */
  compareScenarios: (scenarioIds) => {
    return apiRequest('/scenarios/compare', {
      method: 'POST',
      body: JSON.stringify({ scenario_ids: scenarioIds })
    });
  },
  
  /**
   * Get the result of an asynchronous task
   * @param {string} taskId - Task ID
   * @returns {Promise} Task result or status
   */
  getTaskResult: (taskId) => {
    return apiRequest(`/tasks/${taskId}`);
  }
};

export default apiService;