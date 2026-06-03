import api from './axios'
import type { Booking, PaginatedResponse } from '../types'

export interface TourOrderCreateRequest {
  excursion: number
  slot: number
  first_name: string
  last_name: string
  middle_name?: string
  phone?: string
  email?: string
  num_participants: number
  contact_method: 'call' | 'whatsapp' | 'telegram' | 'email'
  comment?: string
  save_to_profile?: boolean
}

// TODO: ваще полностью надо менять
export interface TourOrderDetail extends Booking {
  excursion: {
    id: number
    title: string
    slug: string
    main_image: string | null
    price: string
    duration: number
  }
  slot: {
    id: number
    date: string
    time: string
  }
  contact_info: {
    first_name: string
    last_name: string
    patronymic?: string
    phone: string
    email: string
    contact_method: string
  }
  history?: Array<{
    status: string
    changed_at: string
    comment?: string
  }>
}

export const bookingsApi = {
  createOrder: async (data: TourOrderCreateRequest): Promise<Booking> => {
    const response = await api.post('/bookings/orders/', data)
    return response.data
  },

  getMyOrders: async (params?: {
    page?: number
    status?: 'new' | 'confirmed' | 'paid' | 'cancelled' | 'completed'
  }): Promise<PaginatedResponse<Booking>> => {
    const response = await api.get('/bookings/my-orders/', { params })
    return response.data
  },

  getOrderDetail: async (id: number): Promise<TourOrderDetail> => {
    const response = await api.get(`/bookings/my-orders/${id}/`)
    return response.data
  },

  cancelOrder: async (
    id: number,
  ): Promise<{ success: boolean; message: string }> => {
    const response = await api.post(`/bookings/my-orders/${id}/cancel/`)
    return response.data
  },
}
