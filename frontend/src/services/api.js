import axios from 'axios';

// Get base URL from environment or default to local backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // Increased to 2 minutes to handle LLM rate limit retries
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request interceptor for logging/tracing and auth
api.interceptors.request.use(
  (config) => {
    config.metadata = { startTime: new Date() };
    // Add Authorization header if token exists
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    const duration = new Date() - response.config.metadata.startTime;
    console.debug(`[API] ${response.config.method?.toUpperCase()} ${response.config.url} took ${duration}ms`);
    return response;
  },
  (error) => {
    let errorMessage = 'An unexpected error occurred';
    
    if (error.response) {
      // Server responded with error status
      errorMessage = error.response.data?.detail || error.response.data?.message || `Server error: ${error.response.status}`;
    } else if (error.request) {
      // Request made but no response received
      errorMessage = 'Unable to connect to backend server. Please verify backend is running on port 8000.';
    } else {
      errorMessage = error.message;
    }
    
    console.error('[API Error]:', errorMessage, error);
    return Promise.reject({ ...error, userMessage: errorMessage });
  }
);

export default api;
