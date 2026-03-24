// Authentication types
export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  full_name: string
  phone?: string
  role?: 'user' | 'company'
}

export interface RegisterResponse {
  id: number
  email: string
  role: string
}

export interface User {
  id: number
  email: string
  full_name: string
  phone?: string
  role: 'user' | 'company' | 'admin' | 'moderator' | 'superadmin'
  status: 'active' | 'inactive' | 'banned'
  created_at: string
  updated_at: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

// Land types
export interface LandFeature {
  land_id: number
  has_water: boolean
  has_electricity: boolean
  has_gas: boolean
  has_roads: boolean
  boundaries_defined: boolean
  build_ready: boolean
  notes?: string
}

export interface Land {
  id: number
  title: string
  description?: string
  address: string
  latitude: number
  longitude: number
  cadastral_number?: string
  price?: number
  area?: number
  land_category?: string
  allowed_usage?: string
  deal_type?: 'purchase' | 'lease' | 'rent' | 'auction'
  listing_type?: 'import' | 'owner' | 'agency'
  has_building?: boolean
  photos?: string[]
  contact_phone?: string
  status: string
  is_actual: boolean
  created_at: string
  updated_at: string
}

export interface LandDetail extends Land {
  external_id?: string
  source_id?: number
  region_id: number
  city_id?: number
  owner_user_id?: number
  published_at?: string
  features?: LandFeature
}

export interface LandsFilterRequest {
  region_id?: number
  city_id?: number
  region_name?: string
  city_name?: string
  price_min?: number
  price_max?: number
  area_min?: number
  area_max?: number
  deal_type?: 'purchase' | 'lease' | 'rent' | 'auction'
  listing_type?: 'import' | 'owner' | 'agency'
  has_building?: boolean
  land_category?: string
  search_query?: string
  cadastral_number?: string
  latitude?: number
  longitude?: number
  bbox_radius_km?: number
  page?: number
  limit?: number
}

// Land companies (relevant contractors)
export interface LandCompanyInfo {
  id: number
  public_name: string
  rating: number
  reviews_count: number
  verification_status: string
  contact_phone?: string
  contact_email?: string
}

export interface ServiceWithCompanies {
  service_id: number
  service_name: string
  priority: string
  companies: LandCompanyInfo[]
}

export interface LandCompaniesResponse {
  land_id: number
  region_id: number
  services_with_companies: ServiceWithCompanies[]
}

export interface LandsListResponse {
  items: Land[]
  total: number
  page: number
  limit: number
  pages: number
}

// Service and Category types
export interface Category {
  id: number
  name: string
  slug: string
  icon?: string
  sort_order: number
  is_active: boolean
}

export interface Service {
  id: number
  name: string
  slug: string
  short_description?: string
  full_description?: string
  is_required_default: boolean
  priority: 'critical' | 'recommended' | 'optional'
  category_id: number
  is_active: boolean
  created_at: string
  updated_at: string
}

// Recommendations types
export interface ServiceRecommendation {
  service_id: number
  service_slug: string
  service_name: string
  priority: 'critical' | 'recommended' | 'optional'
  reason: string
  step_order: number
}

export interface RecommendationsResponse {
  land_id: number
  services: ServiceRecommendation[]
  summary: string
  total_critical: number
  total_recommended: number
  total_optional: number
}

// Land Plan types
export interface LandPlanStep {
  id: number
  land_plan_id: number
  service_id: number
  service_name?: string
  title?: string
  description?: string
  order: number
  priority: string
  status: 'pending' | 'in_progress' | 'completed' | 'skipped'
  selected_company_id?: number
  created_at: string
  updated_at: string
}

export interface LandPlan {
  id: number
  user_id: number
  land_id: number
  status: string
  summary?: string
  created_at: string
  updated_at: string
}

export interface LandPlanDetail extends LandPlan {
  steps: LandPlanStep[]
}

export interface LandPlanCreateRequest {
  land_id: number
  selected_service_ids: number[]
}

// Company types
export interface Company {
  id: number
  legal_name: string
  public_name: string
  description?: string
  logo_url?: string
  contact_phone?: string
  contact_email?: string
  website?: string
  rating: number
  reviews_count: number
  verification_status: 'unverified' | 'pending' | 'verified'
  is_active: boolean
  created_at: string
}

export interface CompanyDetail extends Company {
  services?: CompanyService[]
  region_ids?: number[]
  updated_at: string
}

export interface CompanyService {
  id: number
  service_id: number
  service_name: string
  base_price_from?: number
  is_active: boolean
}

// Application types
export interface Application {
  id: number
  user_id: number
  land_id: number
  service_id: number
  company_id: number
  land_plan_step_id?: number
  status: 'pending' | 'accepted' | 'in_progress' | 'completed' | 'rejected' | 'cancelled'
  message?: string
  created_at: string
  updated_at: string
}

export interface ApplicationDetail extends Application {
  land_title?: string
  service_name?: string
  company_name?: string
  company_phone?: string
  company_email?: string
}

export interface ApplicationCreateRequest {
  land_id: number
  service_id: number
  company_id: number
  land_plan_step_id?: number
  message?: string
}

export interface ApplicationUpdateStatusRequest {
  status: 'pending' | 'accepted' | 'in_progress' | 'completed' | 'rejected' | 'cancelled'
}

export interface ApplicationStats {
  total: number
  pending: number
  accepted: number
  in_progress: number
  completed: number
  rejected: number
  cancelled: number
}

export interface ApplicationsListResponse {
  items: ApplicationDetail[]
  total: number
}

// Review types
export interface Review {
  id: number
  user_id: number
  company_id: number
  rating: number
  text?: string
  status: 'pending' | 'published' | 'rejected'
  is_verified_purchase: boolean
  created_at: string
  updated_at: string
}

export interface ReviewDetail extends Review {
  user_name?: string
  company_name?: string
}

export interface ReviewCreateRequest {
  company_id: number
  rating: number
  text?: string
}

export interface ReviewUpdateRequest {
  rating?: number
  text?: string
}

export interface CompanyReviewsStatsSchema {
  company_id: number
  company_name: string
  average_rating: number
  total_reviews: number
  reviews_by_rating: Record<string, number>
}

// API Response envelope
export interface ApiListResponse<T> {
  items: T[]
  total: number
  page?: number
  limit?: number
  pages?: number
}

export interface ApiResponse<T> {
  data: T
}
