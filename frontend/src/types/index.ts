// Tipos principales para la aplicación Sentrix

export interface User {
  id: number
  email: string
  name: string
  role: UserRole
  avatar?: string
  created_at: string
  last_login?: string
  is_active: boolean
}

export enum UserRole {
  ADMIN = 'ADMIN',
  EXPERT = 'EXPERT',
  USER = 'USER'
}

export interface Detection {
  id: number
  analysis_id: number
  class_name: string
  class_id: number
  confidence: number
  polygon_data: number[][]
  mask_area: number
  location_data?: LocationData
  validation?: DetectionValidation
}

export interface LocationData {
  has_location: boolean
  coordinates?: string
  latitude?: number
  longitude?: number
  accuracy?: string
  source?: string
}

export interface DetectionValidation {
  is_validated: boolean
  expert_validation?: boolean
  expert_notes?: string
  validated_by?: number
  validated_at?: string
}

export interface Analysis {
  id: number
  image_path: string
  user_id: number
  total_detections: number
  risk_level: RiskLevel
  confidence_threshold: number
  created_at: string
  processing_time_ms?: number
  has_gps_data: boolean
  detections?: Detection[]
}

export enum RiskLevel {
  ALTO = 'ALTO',
  MEDIO = 'MEDIO',
  BAJO = 'BAJO',
  MINIMO = 'MINIMO'
}

export interface AnalysisCreate {
  image: File
  confidence_threshold?: number
  include_gps?: boolean
}

export interface AnalysisResponse {
  id: number
  message: string
  analysis: Analysis
  detections: Detection[]
}

export interface RiskAssessment {
  level: RiskLevel
  high_risk_sites: number
  medium_risk_sites: number
  recommendations: string[]
  total_detections: number
}

export interface UploadProgress {
  loaded: number
  total: number
  percentage: number
}

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  pages: number
}

export interface AnalysisFilters {
  risk_level?: RiskLevel
  date_from?: string
  date_to?: string
  user_id?: number
  has_gps?: boolean
  validated_only?: boolean
}

export interface StatisticsData {
  total_analyses: number
  total_detections: number
  risk_distribution: Record<RiskLevel, number>
  recent_activity: RecentActivity[]
  top_locations: LocationStats[]
}

export interface RecentActivity {
  id: number
  type: 'analysis' | 'validation' | 'report'
  description: string
  user_name: string
  created_at: string
}

export interface LocationStats {
  coordinates: string
  count: number
  risk_level: RiskLevel
  last_detection: string
}

export interface MapMarker {
  id: number
  position: [number, number]
  risk_level: RiskLevel
  detection_count: number
  last_analysis: string
  popup_content?: string
}

export interface ExportOptions {
  format: 'json' | 'csv' | 'pdf'
  filters?: AnalysisFilters
  include_images?: boolean
  include_detections?: boolean
}

export interface NotificationData {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  duration?: number
  persistent?: boolean
}

export interface FormState<T> {
  data: T
  errors: Record<keyof T, string>
  isSubmitting: boolean
  isValid: boolean
}

export interface BreadcrumbItem {
  label: string
  href?: string
  current?: boolean
}

export interface TabItem {
  id: string
  label: string
  icon?: React.ComponentType<{ className?: string }>
  content: React.ReactNode
  disabled?: boolean
}

// Tipos para configuración de la aplicación
export interface AppConfig {
  api: {
    baseUrl: string
    timeout: number
  }
  auth: {
    tokenKey: string
    refreshTokenKey: string
  }
  features: {
    offlineMode: boolean
    realTimeUpdates: boolean
    analytics: boolean
  }
  ui: {
    defaultPageSize: number
    mapDefaultZoom: number
    mapDefaultCenter: [number, number]
  }
}

// Tipos para el estado global
export interface AppState {
  user: User | null
  isAuthenticated: boolean
  theme: 'light' | 'dark' | 'system'
  sidebarOpen: boolean
  notifications: NotificationData[]
}

export interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isLoading: boolean
  error: string | null
}

export interface AnalysisState {
  analyses: Analysis[]
  currentAnalysis: Analysis | null
  filters: AnalysisFilters
  isLoading: boolean
  error: string | null
  pagination: {
    page: number
    total: number
    pages: number
  }
}

// Tipos para hooks personalizados
export interface UseFileUploadOptions {
  accept?: string
  maxSize?: number
  multiple?: boolean
  onProgress?: (progress: UploadProgress) => void
  onError?: (error: string) => void
  onSuccess?: (result: any) => void
}

export interface UseGeolocationOptions {
  enableHighAccuracy?: boolean
  timeout?: number
  maximumAge?: number
}

export interface GeolocationState {
  loading: boolean
  accuracy?: number
  altitude?: number | null
  altitudeAccuracy?: number | null
  heading?: number | null
  latitude?: number
  longitude?: number
  speed?: number | null
  timestamp?: number
  error?: string
}

// Tipos adicionales para UploadsPage
export interface AnalysisResult {
  id: number
  message: string
  analysis: Analysis
  detections: Detection[]
}