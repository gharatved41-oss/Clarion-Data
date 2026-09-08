/**
 * Centralized API Service Layer for Clarion Data / Automated Insight Analyst.
 * Dispatches requests to the FastAPI backend with comprehensive error handling.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

/**
 * Standard HTTP response handler with detailed error extraction.
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const res = await fetch(url, {
      headers: {
        'Accept': 'application/json',
        ...(options.headers || {}),
      },
      ...options,
    });

    if (!res.ok) {
      let errorMsg = `HTTP ${res.status} ${res.statusText}`;
      try {
        const errorJson = await res.json();
        errorMsg = errorJson.detail || errorJson.error || errorJson.message || errorMsg;
      } catch (e) {
        // Response was not JSON
      }
      const err = new Error(errorMsg);
      err.status = res.status;
      throw err;
    }

    // If streaming response or file download
    const contentType = res.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      return await res.json();
    }
    return res;
  } catch (err) {
    console.error(`API Request failed for [${endpoint}]:`, err);
    throw err;
  }
}

export const api = {
  // --------------------------------------------------------------------------
  // System Health
  // --------------------------------------------------------------------------
  getHealth: () => request('/health'),

  // --------------------------------------------------------------------------
  // Dataset Ingestion & Overview
  // --------------------------------------------------------------------------
  uploadDataset: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return request('/upload', {
      method: 'POST',
      body: formData,
      // Do not set Content-Type header so browser sets boundary automatically
      headers: {},
    });
  },

  getOverview: (datasetId) => request(`/dataset/${datasetId}/overview`),

  // --------------------------------------------------------------------------
  // Person 1 Analytical Pipeline
  // --------------------------------------------------------------------------
  getSchema: (datasetId) => request(`/dataset/${datasetId}/schema`),

  getCleaningReport: (datasetId, reclean = false) => 
    request(`/dataset/${datasetId}/cleaning-report?reclean=${reclean}`),

  getAnalysis: (datasetId) => request(`/dataset/${datasetId}/analysis`),

  getCorrelations: (datasetId, method = 'pearson') => 
    request(`/dataset/${datasetId}/correlations?method=${method}`),

  getOutliers: (datasetId, method = 'all', zThreshold = 3.0, contamination = 0.05) => 
    request(`/dataset/${datasetId}/outliers?method=${method}&z_threshold=${zThreshold}&contamination=${contamination}`),

  getVisualizations: (datasetId) => request(`/dataset/${datasetId}/visualizations`),

  getInsights: (datasetId) => request(`/dataset/${datasetId}/insights`),

  getExportUrl: (datasetId, format = 'csv') => 
    `${API_BASE_URL}/dataset/${datasetId}/export?format=${format}`,

  // --------------------------------------------------------------------------
  // Person 2 Intelligence & Advanced Analytics
  // --------------------------------------------------------------------------
  getClusters: (datasetId) => request(`/dataset/${datasetId}/clusters`),

  getPredictions: (datasetId) => request(`/dataset/${datasetId}/predictions`),

  getCharts: (datasetId) => request(`/dataset/${datasetId}/charts`),

  getChartOptions: (datasetId) => request(`/dataset/${datasetId}/chart-options`),

  getDomain: (datasetId) => request(`/dataset/${datasetId}/domain`),

  getPaymentAnalytics: (datasetId) => request(`/dataset/${datasetId}/payment-analytics`),

  getChanges: (datasetId) => request(`/dataset/${datasetId}/changes`),

  getSummary: (datasetId) => request(`/dataset/${datasetId}/summary`),

  getNotifications: (datasetId) => request(`/dataset/${datasetId}/notifications`),

  getDataQuality: (datasetId) => request(`/dataset/${datasetId}/data-quality`),

  getDashboard: (datasetId) => request(`/dataset/${datasetId}/dashboard`),

  // --------------------------------------------------------------------------
  // AI Assistant & Copilot Chatbot
  // --------------------------------------------------------------------------
  sendChatMessage: (datasetId, message) => 
    request('/chat/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dataset_id: datasetId, message }),
    }),

  getChatHistory: (datasetId) => request(`/chat/history/${datasetId}`),

  applyDiff: (filePath, diffContent, description = '') => 
    request('/chat/apply-diff', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        file_path: filePath,
        diff: diffContent,
        description,
      }),
    }),
};

export default api;
