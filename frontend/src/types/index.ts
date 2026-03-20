// Auth
export interface User {
  id: string
  email: string
  full_name: string
  organization?: string
  is_active: boolean
  created_at: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

// Assets
export interface Asset {
  id: string
  name: string
  asset_type: string
  location_name?: string
  latitude?: number
  longitude?: number
  description?: string
  risk_score: number
  created_at: string
}

export interface AssetCreate {
  name: string
  asset_type: string
  location_name?: string
  latitude?: number
  longitude?: number
  description?: string
}

// Inspections
export type InspectionStatus = 'pending' | 'processing' | 'completed' | 'failed'
export type DefectSeverity = 'low' | 'medium' | 'high' | 'critical'

export interface Defect {
  id: string
  defect_type: string
  severity: DefectSeverity
  confidence: number
  bbox?: { x1: number; y1: number; x2: number; y2: number }
  description?: string
  recommendation?: string
}

export interface Inspection {
  id: string
  title: string
  status: InspectionStatus
  image_count: number
  risk_score?: number
  defect_count: number
  processing_duration_ms?: number
  error_message?: string
  created_at: string
  completed_at?: string
  defects: Defect[]
}

export interface InspectionListItem {
  id: string
  title: string
  status: InspectionStatus
  image_count: number
  risk_score?: number
  defect_count: number
  created_at: string
}

// Analytics
export interface DashboardStats {
  total_inspections: number
  total_assets: number
  total_defects: number
  critical_defects: number
  avg_risk_score: number
  inspections_this_month: number
}

export interface RiskSummary {
  asset_id: string
  asset_name: string
  risk_score: number
  defect_count: number
  last_inspection?: string
}

// Pagination
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

// API Error
export interface ApiError {
  detail: string
  status?: number
}
