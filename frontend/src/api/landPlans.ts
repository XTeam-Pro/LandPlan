import { apiClient } from './client'
import { LandPlanCreateRequest, LandPlanDetail } from '@/types'

export const landPlansApi = {
  create: async (data: LandPlanCreateRequest): Promise<LandPlanDetail> => {
    const response = await apiClient.post<LandPlanDetail>('/api/v1/land-plans', data)
    return response.data
  },

  getById: async (id: number): Promise<LandPlanDetail> => {
    const response = await apiClient.get<LandPlanDetail>(`/api/v1/land-plans/${id}`)
    return response.data
  },

  getMyPlans: async (): Promise<LandPlanDetail[]> => {
    const response = await apiClient.get<LandPlanDetail[]>('/api/v1/my-land-plans')
    return response.data
  },

  updateStep: async (stepId: number, data: { status?: string; selected_company_id?: number }) => {
    const response = await apiClient.patch(`/api/v1/land-plan-steps/${stepId}`, data)
    return response.data
  },

  completeStep: async (stepId: number) => {
    const response = await apiClient.post(`/api/v1/land-plan-steps/${stepId}/complete`)
    return response.data
  },
}

export default landPlansApi
