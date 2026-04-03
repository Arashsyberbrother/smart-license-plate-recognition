import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

apiClient.interceptors.request.use(
  (config) => {
    const apiKey = sessionStorage.getItem('api_key');
    if (apiKey) {
      config.headers['X-API-Key'] = apiKey;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'خطای ناشناخته رخ داد';
    console.error('API Error:', message);
    return Promise.reject(new Error(message));
  }
);

export const detectPlate = (formData) =>
  apiClient.post('/api/plates/detect', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

export const getPlates = (params = {}) =>
  apiClient.get('/api/plates', { params });

export const getPlate = (id) =>
  apiClient.get(`/api/plates/${id}`);

export const deletePlate = (id) =>
  apiClient.delete(`/api/plates/${id}`);

export const getDashboardStats = () =>
  apiClient.get('/api/dashboard/stats');

export const getAnalyticsDaily = (days = 7) =>
  apiClient.get('/api/analytics/daily', { params: { days } });

export const getAnalyticsDistribution = () =>
  apiClient.get('/api/analytics/distribution');

export const getHealth = () =>
  apiClient.get('/api/health');

export default apiClient;
