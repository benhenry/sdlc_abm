/**
 * API client for SDLC SimLab backend
 *
 * Axios-based client with TypeScript support.
 */

import axios, { AxiosInstance, AxiosError } from 'axios'
import type { ApiError } from '../types'

// Get API URL from environment or use default
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add any auth tokens here if needed in the future
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    // Handle specific error cases
    if (error.response) {
      // Server responded with error status
      const apiError: ApiError = {
        detail: error.response.data?.detail || 'An error occurred',
        error_type: error.response.data?.error_type,
        timestamp: error.response.data?.timestamp,
      }
      return Promise.reject(apiError)
    } else if (error.request) {
      // Request made but no response
      return Promise.reject({
        detail: 'No response from server. Please check your connection.',
        error_type: 'NetworkError',
      })
    } else {
      // Error in request setup
      return Promise.reject({
        detail: error.message || 'Unknown error occurred',
        error_type: 'RequestError',
      })
    }
  }
)

export default apiClient
export { API_URL }
