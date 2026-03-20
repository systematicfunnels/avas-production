import axios, { AxiosInstance, AxiosError } from 'axios'
import type {
  TokenResponse, User, Asset, AssetCreate,
  Inspection, InspectionListItem, DashboardStats,
  RiskSummary, PaginatedResponse
} from '@/types'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: `${API_URL}/api/v1`,
      timeout: 30000,
      headers: { 'Content-Type': 'application/json' },
    })

    // Attach token to every request
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token')
      if (token) config.headers.Authorization = `Bearer ${token}`
      return config
    })

    // Handle 401 — clear session and redirect to login
    this.client.interceptors.response.use(
      (res) => res,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  // ---- Auth ----
  async register(email: string, password: string, full_name: string, organization?: string): Promise<User> {
    const { data } = await this.client.post<User>('/auth/register', { email, password, full_name, organization })
    return data
  }

  async login(email: string, password: string): Promise<TokenResponse> {
    const { data } = await this.client.post<TokenResponse>('/auth/login', { email, password })
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    return data
  }

  logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token')
  }

  // ---- Assets ----
  async listAssets(): Promise<Asset[]> {
    const { data } = await this.client.get<Asset[]>('/assets')
    return data
  }

  async createAsset(payload: AssetCreate): Promise<Asset> {
    const { data } = await this.client.post<Asset>('/assets', payload)
    return data
  }

  async getAsset(id: string): Promise<Asset> {
    const { data } = await this.client.get<Asset>(`/assets/${id}`)
    return data
  }

  async deleteAsset(id: string): Promise<void> {
    await this.client.delete(`/assets/${id}`)
  }

  // ---- Inspections ----
  async createInspection(title: string, asset_id?: string): Promise<Inspection> {
    const { data } = await this.client.post<Inspection>('/inspections', { title, asset_id })
    return data
  }

  async uploadImages(inspectionId: string, files: File[], onProgress?: (pct: number) => void): Promise<any> {
    const form = new FormData()
    files.forEach((f) => form.append('files', f))
    const { data } = await this.client.post(`/inspections/${inspectionId}/upload`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (onProgress && e.total) onProgress(Math.round((e.loaded * 100) / e.total))
      },
    })
    return data
  }

  async analyzeInspection(inspectionId: string): Promise<{ message: string; status: string }> {
    const { data } = await this.client.post(`/inspections/${inspectionId}/analyze`)
    return data
  }

  async listInspections(page = 1, pageSize = 20): Promise<PaginatedResponse<InspectionListItem>> {
    const { data } = await this.client.get<PaginatedResponse<InspectionListItem>>(
      `/inspections?page=${page}&page_size=${pageSize}`
    )
    return data
  }

  async getInspection(id: string): Promise<Inspection> {
    const { data } = await this.client.get<Inspection>(`/inspections/${id}`)
    return data
  }

  // ---- Analytics ----
  async getDashboardStats(): Promise<DashboardStats> {
    const { data } = await this.client.get<DashboardStats>('/analytics/dashboard')
    return data
  }

  async getRiskSummary(): Promise<RiskSummary[]> {
    const { data } = await this.client.get<RiskSummary[]>('/analytics/risk-summary')
    return data
  }
}

export const api = new ApiClient()
