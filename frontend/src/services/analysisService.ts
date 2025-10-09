import { apiClient } from '@/api/client'
import { apiEndpoints } from '@/lib/config'
import type { 
  Analysis, 
  AnalysisFilters, 
  PaginatedResponse, 
  Detection,
  ValidationStatus 
} from '@/types'

// Request/Response Types
export interface AnalysisUploadData {
  file: File
  confidence_threshold?: number
  include_gps?: boolean
  latitude?: number
  longitude?: number
}

export interface BatchUploadOptions {
  confidence_threshold?: number
  include_gps?: boolean
  latitude?: number
  longitude?: number
}

export interface BatchUploadData {
  files: File[]
  options?: BatchUploadOptions
}

export interface AnalysisResponse {
  id: number
  message: string
  analysis: Analysis
  detections: Detection[]
}

export interface BatchAnalysisResponse {
  results: AnalysisResponse[]
  total_processed: number
  successful: number
  failed: number
  errors: string[]
}

export interface DetectionValidationData {
  validation_status: ValidationStatus
  validation_notes?: string
}

export interface BatchValidationData {
  detection_ids: string[]
  validation_status: ValidationStatus
  validation_notes?: string
}

export interface ExportOptions {
  format: 'json' | 'csv' | 'pdf'
  include_images?: boolean
  include_detections?: boolean
}

// Analysis Service
export const analysisService = {
  // Analysis CRUD operations
  getAnalyses: (filters?: AnalysisFilters): Promise<PaginatedResponse<Analysis>> => {
    const params: Record<string, string> = {}
    
    if (filters) {
      if (filters.risk_level) params.risk_level = filters.risk_level
      if (filters.date_from) params.date_from = filters.date_from
      if (filters.date_to) params.date_to = filters.date_to
      if (filters.user_id) params.user_id = filters.user_id.toString()
      if (filters.has_gps !== undefined) params.has_gps = filters.has_gps.toString()
      if (filters.validated_only !== undefined) params.validated_only = filters.validated_only.toString()
    }

    return apiClient.get(apiEndpoints.analyses.list, params)
  },

  getAnalysis: (id: string): Promise<Analysis> => {
    return apiClient.get(apiEndpoints.analyses.detail(id))
  },

  deleteAnalysis: (id: string): Promise<void> => {
    return apiClient.delete(apiEndpoints.analyses.detail(id))
  },

  // Upload operations
  uploadAnalysis: (data: AnalysisUploadData): Promise<AnalysisResponse> => {
    const formData = new FormData()
    formData.append('file', data.file)

    if (data.confidence_threshold !== undefined) {
      formData.append('confidence_threshold', data.confidence_threshold.toString())
    }
    if (data.include_gps !== undefined) {
      formData.append('include_gps', data.include_gps.toString())
    }
    if (data.latitude !== undefined) {
      formData.append('latitude', data.latitude.toString())
    }
    if (data.longitude !== undefined) {
      formData.append('longitude', data.longitude.toString())
    }

    return apiClient.post(apiEndpoints.analyses.create, formData)
  },

  batchUpload: (data: BatchUploadData): Promise<BatchAnalysisResponse> => {
    const formData = new FormData()
    
    // Add files
    data.files.forEach((file) => {
      formData.append('files', file)
    })

    // Add options
    if (data.options?.confidence_threshold !== undefined) {
      formData.append('confidence_threshold', data.options.confidence_threshold.toString())
    }
    if (data.options?.include_gps !== undefined) {
      formData.append('include_gps', data.options.include_gps.toString())
    }
    if (data.options?.latitude !== undefined) {
      formData.append('latitude', data.options.latitude.toString())
    }
    if (data.options?.longitude !== undefined) {
      formData.append('longitude', data.options.longitude.toString())
    }

    return apiClient.post(apiEndpoints.analyses.batch, formData)
  },

  // Image operations
  getAnalysisImage: (id: string): Promise<Blob> => {
    return apiClient.get(apiEndpoints.analyses.image(id))
  },

  // Export operations
  exportAnalysis: (id: string, options?: ExportOptions): Promise<Blob> => {
    const params: Record<string, string> = {}
    
    if (options) {
      if (options.format) params.format = options.format
      if (options.include_images !== undefined) params.include_images = options.include_images.toString()
      if (options.include_detections !== undefined) params.include_detections = options.include_detections.toString()
    }

    return apiClient.get(apiEndpoints.analyses.export(id), params)
  },

  // Detection operations
  getDetectionsByAnalysis: (analysisId: string): Promise<Detection[]> => {
    return apiClient.get(apiEndpoints.detections.byAnalysis(analysisId))
  },

  validateDetection: (id: string, data: DetectionValidationData): Promise<Detection> => {
    return apiClient.put(apiEndpoints.detections.validate(id), data)
  },

  getPendingDetections: (): Promise<Detection[]> => {
    return apiClient.get(apiEndpoints.detections.pending)
  },

  batchValidateDetections: (data: BatchValidationData): Promise<Detection[]> => {
    return apiClient.post(apiEndpoints.detections.batchValidate, data)
  },

  // Map data operations
  getHeatmapData: (filters?: AnalysisFilters): Promise<any> => {
    const params: Record<string, string> = {}
    
    if (filters) {
      if (filters.risk_level) params.risk_level = filters.risk_level
      if (filters.date_from) params.date_from = filters.date_from
      if (filters.date_to) params.date_to = filters.date_to
    }

    return apiClient.get(apiEndpoints.analyses.heatmapData, params)
  },

  getMapStats: (filters?: AnalysisFilters): Promise<any> => {
    const params: Record<string, string> = {}
    
    if (filters) {
      if (filters.risk_level) params.risk_level = filters.risk_level
      if (filters.date_from) params.date_from = filters.date_from
      if (filters.date_to) params.date_to = filters.date_to
    }

    return apiClient.get(apiEndpoints.analyses.mapStats, params)
  },
} as const