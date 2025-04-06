import axios from 'axios';

const api = axios.create({
  // Use NEXT_PUBLIC_ prefix for client-side access in Next.js
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
});

// Optional: intercept responses to handle errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // transform Keycloak or FastAPI error messages
    console.error('API Error:', error);
    const errMsg = error.response?.data?.detail || error.message || 'An unknown error occurred';
    // Here you might want to show a notification to the user
    return Promise.reject(errMsg);
  }
);

export default api;
