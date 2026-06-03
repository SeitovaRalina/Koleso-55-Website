import api from './axios'
import type { PaginatedResponse } from '../types'

export const wishlistApi = {
  getWishlist: async (params?: { page?: number }): Promise<PaginatedResponse<Wishlist>> => {
    const response = await api.get('/wishlist/', { params })
    return response.data
  },

  addToWishlist: async (excursionId: number) => {
    const response = await api.post('/wishlist/add/', { excursion_id: excursionId })
    return response.data
  },

  removeFromWishlist: async (excursionId: number) => {
    const response = await api.delete(`/wishlist/${excursionId}/`)
    return response.data
  },

  checkInWishlist: async (excursionId: number): Promise<{ is_in_wishlist: boolean }> => {
    const response = await api.get(`/wishlist/check/${excursionId}/`)
    return response.data
  },
}
