import api from './axios'
import type { PaginatedResponse } from '../types'

export interface InquiryPayload {
  request_id: string
  excursion: number
  name: string
  phone?: string
  email?: string
  contact_method: 'call' | 'whatsapp' | 'telegram' | 'max' | 'email'
  question: string
}

export interface MyInquiry {
  id: number
  excursion: number
  excursion_title: string
  question: string
  created_at: string
  public_status: string
}

export const inquiriesApi = {
  create: async (payload: InquiryPayload): Promise<{ id: number }> => {
    const response = await api.post('/excursions/inquiries/', payload)
    return response.data
  },
  listMine: async (page = 1): Promise<PaginatedResponse<MyInquiry>> => {
    const response = await api.get('/excursions/inquiries/', { params: { page } })
    return response.data
  },
}
