import axios from 'axios'
import type { Recommendation } from '../types'

const RECOMMENDER_URL =
  import.meta.env.VITE_RECOMMENDER_URL || 'http://localhost:8002/api/v1'

export const recommendationsApi = {
  getUserRecommendations: async (
    userId: number,
    topK: number = 20,
    excludeInteracted: boolean = true,
  ): Promise<Recommendation[]> => { //TODO: тут на выходе модель ваще другая, такая как ниже
    const response = await axios.get(
      `${RECOMMENDER_URL}/recommendations/user/${userId}`,
      {
        params: { top_k: topK , exclude_interacted: excludeInteracted},
      },
    )
    return response.data
  },

  // TODO: response должен быть такой
  // {
  //   "recommendations": [
  //     {
  //       "excursion_id": 0,
  //       "score": 1,
  //       "title": "string",
  //       "category": "string",
  //       "price": 0
  //     }
  //   ],
  //   "user_id": 0,
  //   "session_id": "string",
  //   "algorithm_used": "hybrid"
  // }
  getSessionRecommendations: async (
    sessionId: string,
    topK: number = 20,
  ): Promise<Recommendation[]> => {
    const response = await axios.get(`${RECOMMENDER_URL}/recommendations/`, {
      params: { session_id: sessionId, top_k: topK },
    })
    return response.data
  },


  // TODO: response должен быть такой
  // {
  //   "similar_excursions": [
  //     {
  //       "excursion_id": 0,
  //       "score": 1,
  //       "title": "string",
  //       "category": "string",
  //       "price": 0
  //     }
  //   ],
  //   "excursion_id": 0,
  //   "algorithm_used": "content_based"
  // }
  getSimilarExcursions: async (
    excursionId: number,
    topK: number = 10,
  ): Promise<Recommendation[]> => {
    const response = await axios.get(
      `${RECOMMENDER_URL}/similar/${excursionId}`,
      {
        params: { top_k: topK },
      },
    )
    return response.data
  },
}
