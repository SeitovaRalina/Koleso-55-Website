import api from './axios'
import type { NewsArticle, NewsArticleDetail, NewsCategory, PaginatedResponse } from '../types'

export const newsApi = {
  getNews: async (page: number, category?: string): Promise<PaginatedResponse<NewsArticle>> => {
    const response = await api.get('/news/', { params: { page, category } })
    return response.data
  },
  getCategories: async (): Promise<NewsCategory[]> => {
    const response = await api.get('/news/categories/')
    return response.data
  },
  getArticle: async (slug: string): Promise<NewsArticleDetail> => {
    const response = await api.get(`/news/${encodeURIComponent(slug)}/`)
    return response.data
  },
}
