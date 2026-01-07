import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    console.log('Making request to:', config.url);
    console.log('Token in localStorage:', token ? 'Present' : 'Missing');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('Authorization header set');
    } else {
      console.log('No token - request will fail if endpoint requires auth');
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (userData) => api.post('/auth/register', userData),
  login: (credentials) => api.post('/auth/login', credentials),
  getCurrentUser: () => api.get('/auth/me'),
  getAllUsers: () => api.get('/auth/users'),
};

export const expenseAPI = {
  getAll: (params) => api.get('/expenses/', { params }),
  create: (expenseData) => api.post('/expenses/', expenseData),
  getById: (id) => api.get(`/expenses/${id}`),
  update: (id, expenseData) => api.put(`/expenses/${id}`, expenseData),
  delete: (id) => api.delete(`/expenses/${id}`),
  getSummary: () => api.get('/expenses/summary'),
};

export const analyticsAPI = {
  getPredictions: (days = 30) => api.get(`/analytics/predict?days=${days}`),
  getTrends: (period = 'monthly') => api.get(`/analytics/trends?period=${period}`),
  getCategoryAnalysis: () => api.get('/analytics/category-analysis'),
};

export default api;
