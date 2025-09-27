import axios from 'axios'
import { env } from '@/lib/config'

// Create dedicated YOLO service client
export const yoloClient = axios.create({
  baseURL: env.yoloServiceUrl,
  timeout: 60000, // 60 seconds for AI processing
  headers: {
    'Content-Type': 'multipart/form-data',
  },
})

// YOLO service types
export interface YoloDetection {
  class_name: string
  class_id: number
  confidence: number
  risk_level: string
  breeding_site_type: string
  polygon: number[][]
  mask_area: number
}

export interface YoloLocationInfo {
  has_location: boolean
  latitude?: number
  longitude?: number
  altitude_meters?: number
  location_source?: string
}

export interface YoloCameraInfo {
  camera_make?: string
  camera_model?: string
  camera_datetime?: string
  camera_software?: string
}

export interface YoloRiskAssessment {
  overall_risk_level: string
  total_detections: number
  high_risk_count: number
  medium_risk_count: number
  low_risk_count: number
  risk_score: number
  risk_distribution: Record<string, number>
}

export interface YoloAnalysisResponse {
  analysis_id: string
  status: string
  detections: YoloDetection[]
  total_detections: number
  risk_assessment: YoloRiskAssessment
  location?: YoloLocationInfo
  camera_info?: YoloCameraInfo
  processing_time_ms: number
  model_used: string
  confidence_threshold: number
}

export interface YoloHealthResponse {
  status: string
  service: string
  version: string
  timestamp: string
  model_available: boolean
  model_path: string
}

export interface YoloModelInfo {
  name: string
  path: string
  size_mb: number
  is_current: boolean
}

export interface YoloModelsResponse {
  available_models: YoloModelInfo[]
  current_model: string
}

// YOLO service API functions
export const yoloApi = {
  // Health check
  health: async (): Promise<YoloHealthResponse> => {
    const response = await yoloClient.get('/health')
    return response.data
  },

  // Detect breeding sites in image
  detect: async (
    file: File,
    options: {
      confidence_threshold?: number
      include_gps?: boolean
    } = {}
  ): Promise<YoloAnalysisResponse> => {
    const formData = new FormData()
    formData.append('file', file)

    if (options.confidence_threshold !== undefined) {
      formData.append('confidence_threshold', options.confidence_threshold.toString())
    }

    if (options.include_gps !== undefined) {
      formData.append('include_gps', options.include_gps.toString())
    }

    const response = await yoloClient.post('/detect', formData)
    return response.data
  },

  // Get available models
  models: async (): Promise<YoloModelsResponse> => {
    const response = await yoloClient.get('/models')
    return response.data
  },

  // Direct detection with progress tracking
  detectWithProgress: async (
    file: File,
    options: {
      confidence_threshold?: number
      include_gps?: boolean
      onProgress?: (progress: number) => void
    } = {}
  ): Promise<YoloAnalysisResponse> => {
    const formData = new FormData()
    formData.append('file', file)

    if (options.confidence_threshold !== undefined) {
      formData.append('confidence_threshold', options.confidence_threshold.toString())
    }

    if (options.include_gps !== undefined) {
      formData.append('include_gps', options.include_gps.toString())
    }

    const response = await yoloClient.post('/detect', formData, {
      onUploadProgress: (progressEvent) => {
        if (options.onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          options.onProgress(progress)
        }
      },
    })

    return response.data
  },
}

// Error handling for YOLO service
yoloClient.interceptors.response.use(
  (response) => response,
  (error) => {
    let errorMessage = 'Error en el servicio YOLO'

    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail
    } else if (error.code === 'ECONNABORTED') {
      errorMessage = 'El procesamiento de IA ha excedido el tiempo límite'
    } else if (error.code === 'NETWORK_ERROR' || !error.response) {
      errorMessage = 'No se puede conectar con el servicio YOLO. Verifica que esté ejecutándose en el puerto 8001.'
    } else {
      switch (error.response?.status) {
        case 400:
          errorMessage = 'Archivo de imagen inválido o parámetros incorrectos'
          break
        case 413:
          errorMessage = 'El archivo es demasiado grande'
          break
        case 415:
          errorMessage = 'Formato de imagen no soportado'
          break
        case 500:
          errorMessage = 'Error interno en el servicio YOLO'
          break
        case 503:
          errorMessage = 'Servicio YOLO temporalmente no disponible'
          break
      }
    }

    return Promise.reject(new Error(errorMessage))
  }
)

export default yoloApi