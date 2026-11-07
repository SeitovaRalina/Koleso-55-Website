import api from './axios'
import type { CustomTourRequest, PaginatedResponse } from '../types'

export type CustomTourRequestPayload = Pick<CustomTourRequest, 'name' | 'phone' | 'email' | 'description'>

export const customTourRequestsApi = {
  create: async (data: CustomTourRequestPayload): Promise<CustomTourRequest> => {
    const response = await api.post('/bookings/custom-tour-requests/', data)
    return response.data
  },
  getMine: async (): Promise<PaginatedResponse<CustomTourRequest>> => {
    const response = await api.get('/bookings/my-custom-tour-requests/')
    return response.data
  },
}
