import { apiClient } from './client'
import { Company, CompanyDetail, ApiListResponse } from '@/types'

export const companiesApi = {
  list: async (filters?: Record<string, any>): Promise<ApiListResponse<Company>> => {
    const response = await apiClient.get<ApiListResponse<Company>>('/api/v1/companies', {
      params: filters,
    })
    return response.data
  },

  getById: async (id: number): Promise<CompanyDetail> => {
    const response = await apiClient.get<CompanyDetail>(`/api/v1/companies/${id}`)
    return response.data
  },

  getByService: async (serviceId: number, regionId?: number): Promise<ApiListResponse<Company>> => {
    const response = await apiClient.get<ApiListResponse<Company>>(
      `/api/v1/companies/by-service/${serviceId}`,
      {
        params: regionId ? { region_id: regionId } : undefined,
      }
    )
    return response.data
  },

  create: async (data: Partial<Company>): Promise<Company> => {
    const response = await apiClient.post<Company>('/api/v1/companies', data)
    return response.data
  },

  update: async (id: number, data: Partial<Company>): Promise<Company> => {
    const response = await apiClient.patch<Company>(`/api/v1/companies/${id}`, data)
    return response.data
  },
}

export default companiesApi
