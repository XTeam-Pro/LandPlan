import { apiClient } from './client'

export interface CompanyInfo {
  company_id: number | null
  company_name?: string
}

export const companyDashboardApi = {
  getMyCompanyInfo: async (): Promise<CompanyInfo> => {
    const response = await apiClient.get<CompanyInfo>('/api/v1/applications/company-info')
    return response.data
  },
}

export default companyDashboardApi
