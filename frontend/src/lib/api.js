/**
 * API configuration with validation
 */

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// Validate backend URL is configured
if (!BACKEND_URL || BACKEND_URL.includes('undefined')) {
  console.error(
    '❌ ERROR: REACT_APP_BACKEND_URL is not configured!',
    'Please set REACT_APP_BACKEND_URL environment variable in Vercel.'
  );
}

export const API_BASE = BACKEND_URL || 'http://localhost:8001';
export const API = `${API_BASE}/api`;

/**
 * Get validated API endpoint
 * @returns {string} API base URL
 */
export function getApiUrl() {
  if (!BACKEND_URL) {
    throw new Error(
      'Backend URL not configured. Set REACT_APP_BACKEND_URL in environment variables.'
    );
  }
  return API;
}
