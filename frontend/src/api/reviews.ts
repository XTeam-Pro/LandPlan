import { apiClient } from './client'
import { ReviewCreateRequest, ReviewDetail, CompanyReviewsStatsSchema } from '@/types'

export interface CompanyReviewsResponse {
  reviews: ReviewDetail[]
  stats: CompanyReviewsStatsSchema
}

export const reviewsApi = {
  getCompanyReviews: async (companyId: number): Promise<CompanyReviewsResponse> => {
    const response = await apiClient.get<CompanyReviewsResponse>(
      `/api/v1/companies/${companyId}/reviews`
    )
    return response.data
  },

  create: async (companyId: number, data: ReviewCreateRequest): Promise<ReviewDetail> => {
    const response = await apiClient.post<ReviewDetail>(
      `/api/v1/companies/${companyId}/reviews`,
      data
    )
    return response.data
  },
}

export default reviewsApi
