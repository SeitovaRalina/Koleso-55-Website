import axios from 'axios'
import {
  getAuthToken,
  getRefreshToken,
  setAuthToken,
  clearAuthTokens,
} from '../utils/session'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  config => {
    const token = getAuthToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error),
)

// Response interceptor to handle token refresh
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      // TODO: Сейчас /accounts/refresh/ принимает в body refresh токен, а возвращает access и refreah токены вместе. Измени реализацию

      try {
        const refreshToken = getRefreshToken()
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/accounts/refresh/`, {
            refresh: refreshToken,
          })

          const { access } = response.data
          setAuthToken(access)

          originalRequest.headers.Authorization = `Bearer ${access}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        clearAuthTokens()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  },
)

export default api
