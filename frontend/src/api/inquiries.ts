import api from './axios'

export interface InquiryPayload {
  request_id: string
  excursion: number
  name: string
  phone: string
  contact_method: 'call' | 'whatsapp' | 'telegram' | 'max'
  question: string
}

export const inquiriesApi = {
  create: async (payload: InquiryPayload): Promise<{ id: number }> => {
    const response = await api.post('/excursions/inquiries/', payload)
    return response.data
  },
}
