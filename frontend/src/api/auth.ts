import api from './axios'
import type { User } from '../types'

export const authApi = {
  login: async (data: {
    contact: string
    contact_type: 'email' | 'phone'
    password: string
  }) => {
    const response = await api.post('/accounts/login/', data)
    return response.data
  },

  register: async (data: {
    email: string
    phone?: string
    password: string
    password2: string
  }) => {
    const response = await api.post('/accounts/register/', data)
    return response.data
  },

  logout: async (refresh: string) => {
    const response = await api.post('/accounts/logout/', { refresh })
    return response.data
  },

  refresh: async (refresh: string) => {
    const response = await api.post('/accounts/refresh/', { refresh })
    return response.data
  },

  getProfile: async (): Promise<User> => {
    const response = await api.get('/accounts/profile/')
    return response.data
  },

  updateProfile: async (data: Partial<User>): Promise<User> => {
    const response = await api.patch('/accounts/profile/', data)
    return response.data
  },

  passwordReset: async (data: {
    contact: string
    contact_type: 'email' | 'phone'
  }) => {
    const response = await api.post('/accounts/password-reset/', data)
    return response.data
  },

  passwordResetConfirm: async (
    uidb64: string,
    token: string,
    data: {
      new_password: string
      new_password2: string
    },
  ) => {
    const response = await api.post(
      `/accounts/password-reset-confirm/${uidb64}/${token}/`,
      { new_password: data.new_password, new_password2: data.new_password2 },
    )
    return response.data
  },

  verifyEmail: async () => {
    const response = await api.post('/accounts/verify-email/')
    return response.data
  },

  verifyEmailConfirm: async (uidb64: string, token: string) => {
    const response = await api.get(`/accounts/verify-email/${uidb64}/${token}/`)
    return response.data
  },

  socialLogin: async (
    provider: 'google' | 'vk',
    data: { access_token?: string; code?: string; id_token?: string },
  ) => {
    const response = await api.post(`/accounts/${provider}/`, data)
    return response.data
  },
}
