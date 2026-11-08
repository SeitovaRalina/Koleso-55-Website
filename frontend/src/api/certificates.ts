import api from './axios'

export interface CertificateRequestInput {
  buyer_name: string
  buyer_phone: string
  buyer_email: string
  recipient_name: string
  recipient_phone: string
  recipient_email: string
  amount: number
  format: 'digital' | 'printed'
  message: string
}

export async function createCertificateRequest(data: CertificateRequestInput): Promise<{ id: number }> {
  const response = await api.post<{ id: number }>('/bookings/certificate-requests/', data)
  return response.data
}
