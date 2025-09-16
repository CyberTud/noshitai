import { API_URL } from '../config';

// Helper function to get auth headers
export const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

// API base configuration
export const apiConfig = {
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  }
};

// Helper for API calls
export const apiCall = async (endpoint, options = {}) => {
  const url = `${API_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      ...apiConfig.headers,
      ...getAuthHeaders(),
      ...options.headers,
    },
  });

  if (!response.ok && response.status !== 401) {
    throw new Error(`API call failed: ${response.statusText}`);
  }

  return response;
};