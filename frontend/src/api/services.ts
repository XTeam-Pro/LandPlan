import { apiClient } from './client'
import { Category, Service } from '@/types'

export const servicesApi = {
  getCategories: async (): Promise<Category[]> => {
    const response = await apiClient.get<Category[]>('/api/v1/categories')
    return response.data
  },

  list: async (categoryId?: number): Promise<Service[]> => {
    const response = await apiClient.get<Service[]>('/api/v1/services', {
      params: categoryId ? { category_id: categoryId } : undefined,
    })
    return response.data
  },

  getById: async (id: number): Promise<Service> => {
    const response = await apiClient.get<Service>(`/api/v1/services/${id}`)
    return response.data
  },
}

export default servicesApi
