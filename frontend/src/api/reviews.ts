import api from './axios'
import type { PaginatedResponse, Review } from '../types'

export const reviewsApi = {
  getExcursionReviews: async (
    excursionId: number,
  ): Promise<PaginatedResponse<Review>> => {
    const response = await api.get(
      `/reviews/excursions/${excursionId}/reviews/`,
    )
    return response.data
  },

  // TODO: в ответе должно быть
  // {
  //   "excursion": 0,
  //   "rating": 5,
  //   "text": "string",
  //   "images": [
  //     {
  //       "id": 0,
  //       "image": "string"
  //     }
  //   ]
  // }
  createReview: async (data: {
    excursion: number
    rating: number
    text: string
    images?: {
      image: File // TODO: File | string
    }[]
  }) => {
    const response = await api.post('/reviews/', data)
    return response.data
  },

  getMyReviews: async (): Promise<Review[]> => {
    const response = await api.get('/reviews/my-reviews/')
    return response.data
  },

  // TODO: нет возможности редактировать отзыв!!!
}
