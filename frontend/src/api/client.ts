import axios, { AxiosResponse, AxiosError } from 'axios'
import { config } from '@/lib/config'
import { useAuthStore } from '@/store/auth'
import { useAppStore } from '@/store/app'

// Create axios instance
export const apiClient = axios.create({
  baseURL: config.api.baseUrl,
  timeout: config.api.timeout,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // Don't override Content-Type for FormData (multipart uploads)
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle auth errors and token refresh
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as any

    // Handle 401 errors (unauthorized)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        await useAuthStore.getState().refreshTokenAction()

        // Retry the original request with new token
        const token = useAuthStore.getState().token
        if (token) {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return apiClient(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        useAuthStore.getState().logout()

        // Redirect to login if not already there
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }

        return Promise.reject(refreshError)
      }
    }

    // Handle other errors
    const errorMessage = getErrorMessage(error)

    // Show global error notification for 5xx errors
    if (error.response?.status && error.response.status >= 500) {
      useAppStore.getState().addNotification({
        type: 'error',
        title: 'Error del servidor',
        message: 'Ha ocurrido un error en el servidor. Por favor, intenta nuevamente.',
        duration: 10000,
      })
    }

    return Promise.reject(new Error(errorMessage))
  }
)

// Helper function to extract error messages
function getErrorMessage(error: AxiosError): string {
  if (error.response?.data) {
    const data = error.response.data as any

    // Check for various error message formats
    if (data.message) return data.message
    if (data.detail) return data.detail
    if (data.error) return data.error
    if (typeof data === 'string') return data
  }

  // Network errors
  if (error.code === 'ECONNABORTED') {
    return 'La solicitud ha excedido el tiempo límite'
  }

  if (error.code === 'NETWORK_ERROR' || !error.response) {
    return 'Error de conexión. Verifica tu conexión a internet.'
  }

  // HTTP status code errors
  switch (error.response?.status) {
    case 400:
      return 'Solicitud inválida'
    case 401:
      return 'No autorizado'
    case 403:
      return 'Acceso denegado'
    case 404:
      return 'Recurso no encontrado'
    case 422:
      return 'Datos de entrada inválidos'
    case 429:
      return 'Demasiadas solicitudes. Intenta nuevamente más tarde.'
    case 500:
      return 'Error interno del servidor'
    case 502:
      return 'Servicio no disponible'
    case 503:
      return 'Servicio temporalmente no disponible'
    default:
      return error.message || 'Ha ocurrido un error inesperado'
  }
}

// Type-safe API response wrapper
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

// Generic API methods
export const api = {
  get: async <T>(url: string, params?: any): Promise<T> => {
    const response = await apiClient.get(url, { params })
    return response.data
  },

  post: async <T>(url: string, data?: any): Promise<T> => {
    const response = await apiClient.post(url, data)
    return response.data
  },

  put: async <T>(url: string, data?: any): Promise<T> => {
    const response = await apiClient.put(url, data)
    return response.data
  },

  patch: async <T>(url: string, data?: any): Promise<T> => {
    const response = await apiClient.patch(url, data)
    return response.data
  },

  delete: async <T>(url: string): Promise<T> => {
    const response = await apiClient.delete(url)
    return response.data
  },

  upload: async <T>(url: string, file: File, onProgress?: (progress: number) => void): Promise<T> => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await apiClient.post(url, formData, {
      headers: {
        // Don't set Content-Type - let browser set it with boundary
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      },
    })

    return response.data
  },

  uploadMultiple: async <T>(
    url: string,
    files: File[],
    onProgress?: (progress: number) => void
  ): Promise<T> => {
    const formData = new FormData()
    files.forEach((file) => {
      formData.append(`files`, file)
    })

    const response = await apiClient.post(url, formData, {
      headers: {
        // Don't set Content-Type - let browser set it with boundary
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      },
    })

    return response.data
  },

  uploadAnalysis: async <T>(
    url: string,
    file: File,
    options?: {
      confidenceThreshold?: number
      includeGps?: boolean
      latitude?: number
      longitude?: number
    },
    onProgress?: (progress: number) => void
  ): Promise<T> => {
    const formData = new FormData()
    formData.append('file', file)

    if (options?.confidenceThreshold !== undefined) {
      formData.append('confidence_threshold', options.confidenceThreshold.toString())
    }

    if (options?.includeGps !== undefined) {
      formData.append('include_gps', options.includeGps.toString())
    }

    if (options?.latitude !== undefined) {
      formData.append('latitude', options.latitude.toString())
    }

    if (options?.longitude !== undefined) {
      formData.append('longitude', options.longitude.toString())
    }

    const response = await apiClient.post(url, formData, {
      headers: {
        // Don't set Content-Type - let browser set it with boundary
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      },
    })

    return response.data
  },

  download: async (url: string, filename?: string): Promise<void> => {
    const response = await apiClient.get(url, {
      responseType: 'blob',
    })

    const blob = new Blob([response.data])
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename || 'download'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)
  },
}

export default api