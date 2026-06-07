import axios from 'axios'
import type { Recommendation } from '../types'

const RECOMMENDER_URL =
  import.meta.env.VITE_RECOMMENDER_URL || 'http://localhost:8002/api/v1'

interface RecommendationResponse {
  recommendations?: Recommendation[]
}

interface SimilarResponse {
  similar_excursions?: Recommendation[]
}

export const recommendationsApi = {
  getUserRecommendations: async (
    userId: number,
    limit: number = 20,
    excludeInteracted: boolean = true,
  ): Promise<Recommendation[]> => {
    const response = await axios.get<RecommendationResponse>(
      `${RECOMMENDER_URL}/recommendations/user/${userId}`,
      {
        params: { limit, exclude_interacted: excludeInteracted },
      },
    )
    return response.data.recommendations || []
  },

  getSessionRecommendations: async (
    sessionId: string,
    limit: number = 20,
  ): Promise<Recommendation[]> => {
    const response = await axios.get<RecommendationResponse>(
      `${RECOMMENDER_URL}/recommendations/`,
      {
        params: { session_id: sessionId, limit },
      },
    )
    return response.data.recommendations || []
  },

  getSimilarExcursions: async (
    excursionId: number,
    limit: number = 10,
  ): Promise<Recommendation[]> => {
    const response = await axios.get<SimilarResponse>(
      `${RECOMMENDER_URL}/similar/${excursionId}`,
      {
        params: { limit },
      },
    )
    return response.data.similar_excursions || []
  },
}
