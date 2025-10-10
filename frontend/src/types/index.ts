// Tipos principales para la aplicación Sentrix

export interface User {
  id: string
  email: string
  display_name?: string
  full_name?: string
  name?: string
  organization?: string
  role: UserRole
  avatar?: string
  created_at: string
  updated_at?: string
  last_login?: string
  is_active: boolean
  is_verified?: boolean
}

export enum UserRole {
  ADMIN = 'admin',
  EXPERT = 'expert',
  USER = 'user'
}

export interface Detection {
  id: string
  analysis_id?: string
  class_name: string
  class_id: number
  confidence: number
  risk_level: RiskLevel
  breeding_site_type: string
  polygon: number[][]
  mask_area: number
  area_square_pixels?: number
  location?: LocationData
  source_filename?: string
  camera_info?: CameraInfo
  validation_status: ValidationStatus
  validation_notes?: string
  validated_at?: string
  created_at: string
}

export interface LocationData {
  has_location: boolean
  latitude?: number
  longitude?: number
  coordinates?: string
  altitude_meters?: number
  location_source?: string
  google_maps_url?: string
  google_earth_url?: string
}

export interface CameraInfo {
  camera_make?: string
  camera_model?: string
  camera_datetime?: string
  camera_software?: string
}

export interface Analysis {
  id: string
  status: string
  image_filename?: string
  image_size_bytes?: number
  location?: LocationData
  camera_info?: CameraInfo
  model_used?: string
  confidence_threshold?: number
  processing_time_ms?: number
  yolo_service_version?: string
  risk_assessment?: RiskAssessment
  detections: Detection[]
  image_taken_at?: string
  created_at: string
  updated_at?: string
}

export enum RiskLevel {
  ALTO = 'ALTO',
  MEDIO = 'MEDIO',
  BAJO = 'BAJO',
  MINIMO = 'MINIMO'
}

export enum ValidationStatus {
  PENDING = 'pending',
  PENDING_VALIDATION = 'pending_validation',
  VALIDATED_POSITIVE = 'validated_positive',
  VALIDATED_NEGATIVE = 'validated_negative',
  REQUIRES_REVIEW = 'requires_review'
}

export enum AnalysisStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  REQUIRES_VALIDATION = 'requires_validation'
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
  level?: RiskLevel
  risk_score?: number
  total_detections: number
  high_risk_count: number
  medium_risk_count: number
  recommendations: string[]
}

export interface UploadProgress {
  loaded: number
  total: number
  percentage: number
}

export interface ApiResponse<T = unknown> {
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


// Tipos para hooks personalizados
export interface UseFileUploadOptions {
  accept?: string
  maxSize?: number
  multiple?: boolean
  onProgress?: (progress: UploadProgress) => void
  onError?: (error: string) => void
  onSuccess?: (result: unknown) => void
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