import { apiClient } from './client'
import {
  Application,
  ApplicationCreateRequest,
  ApplicationDetail,
  ApplicationStats,
  ApplicationUpdateStatusRequest,
  ApplicationsListResponse,
} from '@/types'

export const applicationsApi = {
  create: async (data: ApplicationCreateRequest): Promise<Application> => {
    const response = await apiClient.post<Application>('/api/v1/applications', data)
    return response.data
  },

  list: async (statusFilter?: string): Promise<ApplicationsListResponse> => {
    const response = await apiClient.get<ApplicationsListResponse>('/api/v1/applications', {
      params: statusFilter ? { status_filter: statusFilter } : undefined,
    })
    return response.data
  },

  getById: async (id: number): Promise<ApplicationDetail> => {
    const response = await apiClient.get<ApplicationDetail>(`/api/v1/applications/${id}`)
    return response.data
  },

  updateStatus: async (id: number, data: ApplicationUpdateStatusRequest): Promise<Application> => {
    const response = await apiClient.patch<Application>(
      `/api/v1/applications/${id}/status`,
      data
    )
    return response.data
  },

  getStats: async (): Promise<ApplicationStats> => {
    const response = await apiClient.get<ApplicationStats>('/api/v1/applications/stats')
    return response.data
  },
}

export default applicationsApi
