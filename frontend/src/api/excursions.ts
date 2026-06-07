import api from './axios'
import type { Excursion, ExcursionSlot, PaginatedResponse, Category } from '../types'

export const excursionsApi = {
  getExcursions: async (params?: {
    category?: string | string[]
    date_from?: string
    date_to?: string
    location_type?: string
    min_duration?: number
    max_duration?: number
    min_price?: number
    max_price?: number
    ordering?: string
    page?: number
    search?: string
  }): Promise<PaginatedResponse<Excursion>> => {
    // Ручная сериализация параметров для правильной отправки массивов
    const searchParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (Array.isArray(value)) {
            value.forEach(v => searchParams.append(key, v))
          } else {
            searchParams.append(key, String(value))
          }
        }
      })
    }

    const response = await api.get(`/excursions/?${searchParams.toString()}`)
    return response.data
  },

  getMaxPrice: async (): Promise<number> => {
    // Получаем максимальную цену из всех экскурсий
    const maxPriceResponse = await api.get('/excursions/max-price/')
    return maxPriceResponse.data.max_price || 10000
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

  getCategories: async (): Promise<Category[]> => {
    const response = await api.get('/excursions/categories/')
    // API возвращает пагинированный ответ, извлекаем results
    const data = response.data as PaginatedResponse<Category> | Category[]
    return Array.isArray(data) ? data : data.results
  },
}
