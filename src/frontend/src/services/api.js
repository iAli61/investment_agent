/**
 * Service for API communication
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

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
   * Send a message to the AI assistant
   * @param {string} message - User's message
   * @param {Object} context - Conversation context (optional)
   * @returns {Promise} AI assistant's response
   */
  sendMessage: (message, context = {}) => {
    return apiRequest('/ai/conversation/', {
      method: 'POST',
      body: JSON.stringify({ message, context })
    });
  },
  
  /**
   * Create a streaming connection to the AI assistant
   * @param {string} message - User's message
   * @param {Object} context - Conversation context (optional)
   * @returns {EventSource} SSE connection for streaming responses
   */
  streamConversation: (message, context = {}) => {
    // POST the message first
    const postPromise = fetch(`${API_BASE_URL}/ai/conversation/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message, context })
    });
    
    // Create EventSource for streaming the response
    // This properly handles SSE protocol
    const eventSource = new EventSource(`${API_BASE_URL}/ai/conversation/stream`);
    
    // Return both the eventSource and post promise for proper handling
    return {
      eventSource,
      postPromise
    };
  },
  
  /**
   * Get all properties for a user
   * @param {number} userId - User ID
   * @returns {Promise} List of properties
   */
  getProperties: (userId) => {
    return apiRequest(`/properties?user_id=${userId}`);
  },
  
  /**
   * Get a specific property by ID
   * @param {number} propertyId - Property ID
   * @returns {Promise} Property details
   */
  getPropertyById: (propertyId) => {
    return apiRequest(`/properties/${propertyId}`);
  },
  
  /**
   * Create a new property
   * @param {Object} propertyData - Property details
   * @returns {Promise} Created property
   */
  createProperty: (propertyData) => {
    return apiRequest('/properties', {
      method: 'POST',
      body: JSON.stringify(propertyData)
    });
  },
  
  /**
   * Update an existing property
   * @param {number} propertyId - Property ID
   * @param {Object} propertyData - Updated property data
   * @returns {Promise} Updated property
   */
  updateProperty: (propertyId, propertyData) => {
    return apiRequest(`/properties/${propertyId}`, {
      method: 'PUT',
      body: JSON.stringify(propertyData)
    });
  },
  
  /**
   * Delete a property
   * @param {number} propertyId - Property ID
   * @returns {Promise} Success message
   */
  deleteProperty: (propertyId) => {
    return apiRequest(`/properties/${propertyId}`, {
      method: 'DELETE'
    });
  },
  
  /**
   * Get scenarios for a specific property
   * @param {number} propertyId - Property ID
   * @returns {Promise} List of scenarios
   */
  getPropertyScenarios: (propertyId) => {
    return apiRequest(`/properties/${propertyId}/scenarios`);
  },
  
  /**
   * Create a new scenario for a property
   * @param {number} propertyId - Property ID
   * @param {Object} scenarioData - Scenario data
   * @param {boolean} runAnalysis - Whether to run analysis immediately
   * @returns {Promise} Created scenario
   */
  createPropertyScenario: (propertyId, scenarioData, runAnalysis = false) => {
    return apiRequest(`/properties/${propertyId}/scenarios`, {
      method: 'POST',
      body: JSON.stringify({
        ...scenarioData,
        run_analysis: runAnalysis
      })
    });
  },
  
  /**
   * Get a specific scenario by ID
   * @param {number} scenarioId - Scenario ID
   * @returns {Promise} Scenario data
   */
  getScenarioById: (scenarioId) => {
    return apiRequest(`/scenarios/${scenarioId}`);
  },
  
  /**
   * Update an existing scenario
   * @param {number} scenarioId - Scenario ID
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
   * @param {number} scenarioId - Scenario ID
   * @returns {Promise} Success message
   */
  deleteScenario: (scenarioId) => {
    return apiRequest(`/scenarios/${scenarioId}`, {
      method: 'DELETE'
    });
  },
  
  /**
   * Run analysis on a scenario
   * @param {number} scenarioId - Scenario ID
   * @param {Object} analysisParams - Analysis parameters
   * @param {boolean} runInBackground - Whether to run in background
   * @returns {Promise} Analysis results or status
   */
  analyzeScenario: (scenarioId, analysisParams = {}, runInBackground = true) => {
    return apiRequest(`/scenarios/${scenarioId}/analyze`, {
      method: 'POST',
      body: JSON.stringify({
        ...analysisParams,
        run_in_background: runInBackground
      })
    });
  },
  
  /**
   * Compare multiple scenarios
   * @param {Array} scenarioIds - Array of scenario IDs to compare
   * @returns {Promise} Comparison data
   */
  compareScenarios: (scenarioIds) => {
    // Use query parameter for GET request with array
    const scenarioIdsParam = scenarioIds.join(',');
    return apiRequest(`/scenarios/compare?scenario_ids=${scenarioIdsParam}`);
  },
  
  /**
   * Subscribe to real-time updates via SSE
   * @param {string} clientId - Unique client identifier
   * @param {Object} params - Optional parameters (user_id, property_id, scenario_id)
   * @returns {EventSource} SSE connection for updates
   */
  subscribeToUpdates: (clientId, params = {}) => {
    const { userId, propertyId, scenarioId } = params;
    
    let url = `${API_BASE_URL}/updates/${clientId}`;
    
    // Add optional query parameters
    const queryParams = [];
    if (userId) queryParams.push(`user_id=${userId}`);
    if (propertyId) queryParams.push(`property_id=${propertyId}`);
    if (scenarioId) queryParams.push(`scenario_id=${scenarioId}`);
    
    if (queryParams.length > 0) {
      url = `${url}?${queryParams.join('&')}`;
    }
    
    return new EventSource(url);
  },
  
  /**
   * Get health status of the API
   * @returns {Promise} Health status
   */
  getHealthStatus: () => {
    return apiRequest('/health');
  }
};

export default apiService;