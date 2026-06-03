import api from './axios'

export interface ExcursionViewStartRequest {
  excursion_id: number
  session_id?: string,
  source?: 'catalog' | 'search' | 'recommendation' | 'similar' | 'direct'
}

export interface ExcursionViewHeartbeatRequest {
  view_id: number,
  elapsed_seconds: number
}

export interface ExcursionViewEndRequest {
  view_id: number
}

export const analyticsApi = {
  startView: async (data: ExcursionViewStartRequest) => {
    const response = await api.post('/analytics/view/start/', data)
    return response.data
  },

  heartbeatView: async (data: ExcursionViewHeartbeatRequest) => {
    const response = await api.post('/analytics/view/heartbeat/', data)
    return response.data
  },

  endView: async (data: ExcursionViewEndRequest) => {
    const response = await api.post('/analytics/view/end/', data)
    return response.data
  },

  getSimilarExcursions: async (excursionId: number) => {
    const response = await api.get(`/analytics/recommendations/similar/${excursionId}/`)
    return response.data
  },

  getUserRecommendations: async (userId: number) => {
    const response = await api.get(`/analytics/recommendations/user/${userId}/`)
    return response.data
  },
}
