import { apiClient } from './client'
import { Land, LandDetail, LandFeature, LandsFilterRequest, LandsListResponse, RecommendationsResponse, LandCompaniesResponse } from '@/types'

export const landsApi = {
  list: async (filters?: LandsFilterRequest): Promise<LandsListResponse> => {
    const response = await apiClient.get<LandsListResponse>('/api/v1/lands', {
      params: filters,
    })
    return response.data
  },

  getById: async (id: number): Promise<LandDetail> => {
    const response = await apiClient.get<LandDetail>(`/api/v1/lands/${id}`)
    return response.data
  },

  getFeatures: async (id: number): Promise<LandFeature> => {
    const response = await apiClient.get<LandFeature>(`/api/v1/lands/${id}/features`)
    return response.data
  },

  getRecommendations: async (id: number): Promise<RecommendationsResponse> => {
    const response = await apiClient.get<RecommendationsResponse>(`/api/v1/lands/${id}/recommendations`)
    return response.data
  },

  getCompanies: async (id: number): Promise<LandCompaniesResponse> => {
    const response = await apiClient.get<LandCompaniesResponse>(`/api/v1/lands/${id}/companies`)
    return response.data
  },

  create: async (data: Partial<Land>): Promise<Land> => {
    const response = await apiClient.post<Land>('/api/v1/lands', data)
    return response.data
  },

  update: async (id: number, data: Partial<Land>): Promise<Land> => {
    const response = await apiClient.patch<Land>(`/api/v1/lands/${id}`, data)
    return response.data
  },
}

export default landsApi
