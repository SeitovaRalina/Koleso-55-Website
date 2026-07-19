import api from './axios'
import type { HomepageReview, PaginatedResponse, Review } from '../types'

export const reviewsApi = {
  getHomepageReviews: async (): Promise<HomepageReview[]> => {
    const response = await api.get('/reviews/homepage/')
    return response.data
  },

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

  updateReview: async (
    id: number,
    data: {
      rating?: number
      text?: string
      images?: {
        image: File
      }[]
    },
  ) => {
    const response = await api.patch(`/reviews/${id}/`, data)
    return response.data
  },
}
