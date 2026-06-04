import api from './axios'
import type { Excursion, ExcursionSlot, PaginatedResponse } from '../types'

export const excursionsApi = {
  getExcursions: async (params?: {
    category?: string
    date_from?: string // Corrected type
    date_to?: string // Corrected type
    location_type?: string
    min_duration?: number
    max_duration?: number
    min_price?: number
    max_price?: number
    ordering?: string
    page?: number
    search?: string
  }): Promise<PaginatedResponse<Excursion>> => {
    const response = await api.get('/excursions/', { params })
    return response.data
  },

  getExcursionById: async (id: number): Promise<Excursion> => {
    const response = await api.get(`/excursions/${id}/`)
    return response.data
  },

  getExcursionBySlug: async (slug: string): Promise<Excursion> => {
    const response = await api.get(`/excursions/${slug}/`)
    return response.data
  },

  getSlots: async (excursionId: number, date?: string): Promise<ExcursionSlot[]> => {
    const params = date ? { date } : {}
    const response = await api.get(`/excursions/${excursionId}/slots/`, { params })
    return response.data
  },
}
