import { api } from './client'
import { apiEndpoints } from '@/lib/config'
import type {
  Analysis,
  Detection,
  AnalysisFilters,
  PaginatedResponse,
  AnalysisResponse,
  UploadProgress
} from '@/types'

export interface CreateAnalysisRequest {
  image: File
  confidence_threshold?: number
  include_gps?: boolean
}

export interface BatchAnalysisRequest {
  images: File[]
  confidence_threshold?: number
  include_gps?: boolean
}

export interface AnalysisListParams extends AnalysisFilters {
  page?: number
  per_page?: number
  limit?: number
  sort?: string
  order?: 'asc' | 'desc'
}

export const analysesApi = {
  // List analyses with filters and pagination
  list: async (params?: AnalysisListParams): Promise<PaginatedResponse<Analysis>> => {
    return api.get(apiEndpoints.analyses.list, params)
  },

  // Create new analysis
  create: async (
    data: CreateAnalysisRequest,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<AnalysisResponse> => {
    const formData = new FormData()
    formData.append('file', data.image)

    if (data.confidence_threshold) {
      formData.append('confidence_threshold', data.confidence_threshold.toString())
    }

    if (data.include_gps !== undefined) {
      formData.append('include_gps', data.include_gps.toString())
    }

    return api.upload(apiEndpoints.analyses.create, data.image, (progress) => {
      if (onProgress) {
        onProgress({
          loaded: progress,
          total: 100,
          percentage: progress
        })
      }
    })
  },

  // Batch create analyses
  createBatch: async (
    data: BatchAnalysisRequest,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<AnalysisResponse[]> => {
    return api.uploadMultiple(apiEndpoints.analyses.batch, data.images, (progress) => {
      if (onProgress) {
        onProgress({
          loaded: progress,
          total: 100,
          percentage: progress
        })
      }
    })
  },

  // Get analysis by ID
  getById: async (id: string): Promise<Analysis> => {
    return api.get(apiEndpoints.analyses.detail(id))
  },

  // Get analysis with detections
  getWithDetections: async (id: string): Promise<Analysis & { detections: Detection[] }> => {
    const analysis = await api.get<Analysis>(apiEndpoints.analyses.detail(id))
    const detections = await api.get<Detection[]>(apiEndpoints.detections.byAnalysis(id))
    return { ...analysis, detections }
  },

  // Update analysis
  update: async (id: string, data: Partial<Analysis>): Promise<Analysis> => {
    return api.patch(apiEndpoints.analyses.detail(id), data)
  },

  // Delete analysis
  delete: async (id: string): Promise<void> => {
    return api.delete(apiEndpoints.analyses.detail(id))
  },

  // Export analysis
  export: async (id: string, format: 'json' | 'csv' = 'json'): Promise<void> => {
    const filename = `analysis_${id}.${format}`
    return api.download(`${apiEndpoints.analyses.export(id)}?format=${format}`, filename)
  },

  // Export multiple analyses
  exportBatch: async (
    filters: AnalysisFilters,
    format: 'json' | 'csv' | 'pdf' = 'json'
  ): Promise<void> => {
    const params = new URLSearchParams({ format } as any)
    // Add filter params if they exist
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined) {
        params.append(key, String(value))
      }
    })
    const filename = `analyses_export.${format}`
    return api.download(`${apiEndpoints.analyses.list}/export?${params}`, filename)
  },

  // Get analysis statistics
  getStatistics: async (filters: AnalysisFilters = {}): Promise<{
    total: number
    by_risk_level: Record<string, number>
    by_month: Array<{ month: string; count: number }>
    avg_processing_time: number
    total_detections: number
  }> => {
    return api.get(`${apiEndpoints.analyses.list}/statistics`, filters)
  },

  // Reprocess analysis with different parameters
  reprocess: async (id: string, confidence_threshold?: number): Promise<AnalysisResponse> => {
    return api.post(`${apiEndpoints.analyses.detail(id)}/reprocess`, {
      confidence_threshold
    })
  },

  // Get recent analyses
  getRecent: async (limit: number = 10): Promise<Analysis[]> => {
    return api.get(`${apiEndpoints.analyses.list}/recent`, { limit })
  },

  // Get analyses by user
  getByUser: async (userId: number, params?: AnalysisListParams): Promise<PaginatedResponse<Analysis>> => {
    return api.get(`${apiEndpoints.analyses.list}/user/${userId}`, params)
  },

  // Search analyses
  search: async (query: string, params?: AnalysisListParams): Promise<PaginatedResponse<Analysis>> => {
    return api.get(`${apiEndpoints.analyses.list}/search`, { q: query, ...params })
  },

  // Get analysis processing status
  getProcessingStatus: async (id: string): Promise<{
    status: 'pending' | 'processing' | 'completed' | 'failed'
    progress?: number
    message?: string
  }> => {
    return api.get(`${apiEndpoints.analyses.detail(id)}/status`)
  },

  // Cancel analysis processing
  cancelProcessing: async (id: string): Promise<void> => {
    return api.post(`${apiEndpoints.analyses.detail(id)}/cancel`)
  },

  // Get analyses by risk level
  getByRiskLevel: async (riskLevel: string, limit: number = 50): Promise<Analysis[]> => {
    return api.get(`${apiEndpoints.analyses.list}`, { risk_level: riskLevel, limit })
  },

  // Get analyses with GPS data
  getWithGPS: async (limit: number = 50): Promise<Analysis[]> => {
    return api.get(`${apiEndpoints.analyses.list}`, { has_gps: true, limit })
  },
}