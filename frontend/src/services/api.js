/**
 * API service layer for communicating with the backend
 * Uses Axios for HTTP requests with error handling and interceptors
 */
import axios from 'axios';

// Get API URL from environment or use default
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create Axios instance
const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth tokens or headers here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor with retry logic
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const shouldRetry = (error, retryCount) => {
  // Retry on network errors or 5xx errors
  if (!error.response) return true; // Network error
  if (error.response.status >= 500 && error.response.status < 600) return true; // Server error
  if (error.response.status === 429) return true; // Rate limit
  return false;
};

api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const config = error.config;
    
    // Check if we should retry
    if (config && shouldRetry(error, config.__retryCount || 0)) {
      config.__retryCount = config.__retryCount || 0;
      
      if (config.__retryCount < MAX_RETRIES) {
        config.__retryCount += 1;
        
        // Exponential backoff
        const delay = RETRY_DELAY * Math.pow(2, config.__retryCount - 1);
        await sleep(delay);
        
        return api(config);
      }
    }
    
    // Handle errors with user-friendly messages
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      // Extract user-friendly message
      const message = data?.message || data?.detail || `Error ${status}`;
      
      // Check if this is an expected error that we handle gracefully
      // (e.g., preview endpoint saying campaign needs processing)
      // Check multiple possible URL locations in the error object
      const requestUrl = config?.url || error.config?.url || '';
      const fullUrl = error.request?.responseURL || error.config?.url || '';
      const baseUrl = config?.baseURL || error.config?.baseURL || '';
      const fullRequestUrl = fullUrl || (baseUrl + requestUrl) || '';
      
      // Check if this is a preview endpoint error
      const isPreviewEndpoint = requestUrl.includes('/preview/') || 
                               fullUrl.includes('/preview/') ||
                               fullRequestUrl.includes('/preview/');
      
      // Check if the error message indicates this is an expected "needs processing" error
      const messageLower = message?.toLowerCase() || '';
      const isProcessingError = messageLower.includes('must be processed') ||
                               messageLower.includes('invalid state') ||
                               messageLower.includes('process the campaign') ||
                               messageLower.includes('draft');
      
      // If it's a processing error message, it's almost certainly from preview endpoint
      // Suppress logging for these expected errors (URL check is nice-to-have but message is definitive)
      const isExpectedError = status === 400 && 
                             message &&
                             isProcessingError;
      
      // Create enhanced error with user-friendly message
      error.userMessage = message;
      error.errorDetails = data?.details || null;
      
      // Only log unexpected errors or errors that aren't handled gracefully
      if (!isExpectedError) {
        switch (status) {
          case 400:
            console.error('Bad Request:', data);
            break;
          case 401:
            console.error('Unauthorized:', data);
            break;
          case 404:
            console.error('Not Found:', data);
            break;
          case 422:
            console.error('Validation Error:', data);
            break;
          case 500:
            console.error('Server Error:', data);
            break;
          case 502:
            console.error('Bad Gateway:', data);
            break;
          case 503:
            console.error('Service Unavailable:', data);
            break;
          default:
            console.error('API Error:', data);
        }
      }
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error: No response from server');
      error.userMessage = 'Network error. Please check your connection and try again.';
    } else {
      // Something else happened
      console.error('Error:', error.message);
      error.userMessage = error.message || 'An unexpected error occurred.';
    }
    
    return Promise.reject(error);
  }
);

// API methods

/**
 * Upload campaign assets
 * @param {FormData} formData - Form data containing files and campaign info
 * @returns {Promise} Campaign upload response
 */
export const uploadCampaign = async (formData) => {
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 60000, // 60 seconds for file uploads
  });
  return response.data;
};

/**
 * Process campaign with AI
 * @param {string} campaignId - Campaign ID
 * @returns {Promise} Processing response
 */
export const processCampaign = async (campaignId) => {
  const response = await api.post(`/process/${campaignId}`);
  return response.data;
};

/**
 * Generate proof for campaign
 * @param {string} campaignId - Campaign ID
 * @returns {Promise} Generation response
 */
export const generateProof = async (campaignId) => {
  const response = await api.post(`/generate/${campaignId}`);
  return response.data;
};

/**
 * Get campaign status
 * @param {string} campaignId - Campaign ID
 * @returns {Promise} Status response
 */
export const getCampaignStatus = async (campaignId) => {
  const response = await api.get(`/campaigns/${campaignId}/status`);
  return response.data;
};

/**
 * Get preview data for campaign
 * @param {string} campaignId - Campaign ID
 * @returns {Promise} Preview response
 */
export const getPreview = async (campaignId) => {
  const response = await api.get(`/preview/${campaignId}`);
  return response.data;
};

/**
 * Approve or reject campaign
 * @param {string} campaignId - Campaign ID
 * @param {string} decision - 'approve' or 'reject'
 * @param {string} feedback - Optional feedback or comments
 * @returns {Promise} Approval response
 */
export const approveCampaign = async (campaignId, decision, feedback = null) => {
  const response = await api.post(`/approve/${campaignId}`, { 
    decision,
    feedback: feedback || null
  });
  return response.data;
};

/**
 * Download campaign HTML
 * @param {string} campaignId - Campaign ID
 * @returns {Promise} Download URL or blob
 */
export const downloadCampaign = async (campaignId) => {
  const response = await api.get(`/download/${campaignId}`, {
    responseType: 'blob',
  });
  return response.data;
};

/**
 * List all campaigns
 * @param {Object} params - Query parameters (status, limit, offset, last_n, include_stats)
 * @returns {Promise} Campaign list response
 */
export const listCampaigns = async (params = {}) => {
  const response = await api.get('/campaigns', { params });
  return response.data;
};

/**
 * Get campaign detail by ID
 * @param {string} campaignId - Campaign ID
 * @returns {Promise} Campaign detail response
 */
export const getCampaignDetail = async (campaignId) => {
  const response = await api.get(`/campaigns/${campaignId}`);
  return response.data;
};

/**
 * Reset a rejected campaign to uploaded status
 * @param {string} campaignId - Campaign ID
 * @param {boolean} clearFeedback - Whether to clear feedback
 * @returns {Promise} Updated campaign response
 */
export const resetCampaign = async (campaignId, clearFeedback = false) => {
  const response = await api.post(`/campaigns/${campaignId}/reset`, null, {
    params: { clear_feedback: clearFeedback }
  });
  return response.data;
};

/**
 * Edit campaign content (text fields)
 * @param {string} campaignId - Campaign ID
 * @param {Object} editData - Fields to update (subject_line, preview_text, body_copy, etc.)
 * @returns {Promise} Edit response
 */
export const editCampaignContent = async (campaignId, editData) => {
  const response = await api.post(`/campaigns/${campaignId}/edit`, editData);
  return response.data;
};

/**
 * Replace a campaign image (logo or hero image)
 * @param {string} campaignId - Campaign ID
 * @param {string} imageType - Type: 'logo' or 'hero_{index}' (e.g., 'hero_0')
 * @param {File} file - New image file
 * @returns {Promise} Replace response
 */
export const replaceCampaignImage = async (campaignId, imageType, file) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('image_type', imageType);
  
  const response = await api.post(`/campaigns/${campaignId}/replace-image`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 30000, // 30 seconds for image upload
  });
  return response.data;
};

/**
 * Regenerate campaign proof with updated content/images
 * @param {string} campaignId - Campaign ID
 * @returns {Promise} Preview response with regenerated HTML
 */
export const regenerateProof = async (campaignId) => {
  const response = await api.post(`/campaigns/${campaignId}/regenerate`);
  return response.data;
};

/**
 * Schedule a campaign for future sending
 * @param {string} campaignId - Campaign ID
 * @param {string} scheduledAt - ISO 8601 datetime string
 * @returns {Promise} Schedule response
 */
export const scheduleCampaign = async (campaignId, scheduledAt) => {
  const response = await api.post(`/campaigns/${campaignId}/schedule`, {
    scheduled_at: scheduledAt
  });
  return response.data;
};

/**
 * Cancel a scheduled campaign
 * @param {string} campaignId - Campaign ID
 * @returns {Promise} Cancel response
 */
export const cancelSchedule = async (campaignId) => {
  const response = await api.post(`/campaigns/${campaignId}/cancel-schedule`);
  return response.data;
};

/**
 * Review a campaign (editorial review)
 * @param {string} campaignId - Campaign ID
 * @param {string} reviewStatus - Review status (pending, reviewed, approved, rejected)
 * @param {string} reviewerNotes - Optional reviewer notes
 * @returns {Promise} Review response
 */
export const reviewCampaign = async (campaignId, reviewStatus, reviewerNotes = null) => {
  const response = await api.post(`/campaigns/${campaignId}/review`, {
    review_status: reviewStatus,
    reviewer_notes: reviewerNotes || null
  });
  return response.data;
};

/**
 * List campaigns by review status
 * @param {Object} params - Query parameters (review_status, limit, offset)
 * @returns {Promise} Campaign list response
 */
export const listCampaignsByReviewStatus = async (params = {}) => {
  const response = await api.get('/campaigns/review/list', { params });
  return response.data;
};

/**
 * Update campaign performance metrics
 * @param {string} campaignId - Campaign ID
 * @param {Object} metrics - Performance metrics (open_rate, click_rate, conversion_rate)
 * @returns {Promise} Performance update response
 */
export const updateCampaignPerformance = async (campaignId, metrics) => {
  const response = await api.post(`/campaigns/${campaignId}/performance`, metrics);
  return response.data;
};

/**
 * Get AI-based recommendations for a campaign
 * @param {string} campaignId - Campaign ID
 * @returns {Promise} Recommendations response
 */
export const getRecommendations = async (campaignId) => {
  const response = await api.post(`/campaigns/${campaignId}/recommendations`);
  return response.data;
};

/**
 * Generate campaign data from a natural language prompt
 * @param {string} prompt - Natural language description of the campaign
 * @returns {Promise} Generated campaign data (all form fields)
 */
export const generateCampaignFromPrompt = async (prompt) => {
  const response = await api.post('/campaigns/generate-from-prompt', { prompt });
  return response.data;
};

/**
 * Health check
 * @returns {Promise} Health status
 */
export const healthCheck = async () => {
  const response = await axios.get(`${API_URL}/health`);
  return response.data;
};

export default api;

