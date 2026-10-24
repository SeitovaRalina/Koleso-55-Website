import api from './axios'
import type { NewsArticle, PaginatedResponse } from '../types'

export const newsApi = {
  getNews: async (page: number): Promise<PaginatedResponse<NewsArticle>> => {
    const response = await api.get('/news/', { params: { page } })
    return response.data
  },
}
