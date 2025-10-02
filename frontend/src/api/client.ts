import { config } from '@/lib/config'
import { useAuthStore } from '@/store/auth'
import { useAppStore } from '@/store/app'

// Fetch-based API client
class ApiClient {
  private baseURL: string
  private timeout: number

  constructor(baseURL: string, timeout: number) {
    this.baseURL = baseURL
    this.timeout = timeout
  }

  async request<T = any>(url: string, options: RequestInit = {}): Promise<T> {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), this.timeout)

    try {
      const token = useAuthStore.getState().token
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
        ...options.headers,
      }

      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }

      // Don't override Content-Type for FormData
      if (options.body instanceof FormData) {
        delete (headers as any)['Content-Type']
      }

      const response = await fetch(this.baseURL + url, {
        ...options,
        headers,
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        await this.handleError(response)
      }

      const data = await response.json()
      return data
    } catch (error: any) {
      clearTimeout(timeoutId)
      throw error
    }
  }

  async handleError(response: Response): Promise<never> {
    let errorMessage = 'Error desconocido'

    try {
      const data = await response.json()
      errorMessage = data.message || data.detail || data.error || errorMessage
    } catch {
      errorMessage = response.statusText
    }

    // Handle 401 errors
    if (response.status === 401) {
      try {
        await useAuthStore.getState().refreshTokenAction()
      } catch {
        useAuthStore.getState().logout()
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      }
    }

    // Show global error for 5xx
    if (response.status >= 500) {
      useAppStore.getState().addNotification({
        type: 'error',
        title: 'Error del servidor',
        message: 'Ha ocurrido un error en el servidor. Por favor, intenta nuevamente.',
        duration: 10000,
      })
    }

    throw new Error(errorMessage)
  }

  get<T>(url: string, params?: any): Promise<T> {
    const queryString = params ? '?' + new URLSearchParams(params).toString() : ''
    return this.request<T>(url + queryString, { method: 'GET' })
  }

  post<T>(url: string, data?: any): Promise<T> {
    return this.request<T>(url, {
      method: 'POST',
      body: data instanceof FormData ? data : JSON.stringify(data),
    })
  }

  put<T>(url: string, data?: any): Promise<T> {
    return this.request<T>(url, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  patch<T>(url: string, data?: any): Promise<T> {
    return this.request<T>(url, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  delete<T>(url: string): Promise<T> {
    return this.request<T>(url, { method: 'DELETE' })
  }
}

export const apiClient = new ApiClient(config.api.baseUrl, config.api.timeout)

// Type-safe API response wrapper
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

// Generic API methods
export const api = {
  get: <T>(url: string, params?: any): Promise<T> => apiClient.get<T>(url, params),
  post: <T>(url: string, data?: any): Promise<T> => apiClient.post<T>(url, data),
  put: <T>(url: string, data?: any): Promise<T> => apiClient.put<T>(url, data),
  patch: <T>(url: string, data?: any): Promise<T> => apiClient.patch<T>(url, data),
  delete: <T>(url: string): Promise<T> => apiClient.delete<T>(url),

  upload: async <T>(url: string, file: File, onProgress?: (progress: number) => void): Promise<T> => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post<T>(url, formData)
  },

  uploadMultiple: async <T>(url: string, files: File[], onProgress?: (progress: number) => void): Promise<T> => {
    const formData = new FormData()
    files.forEach((file) => formData.append(`files`, file))
    return apiClient.post<T>(url, formData)
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

    return apiClient.post<T>(url, formData)
  },

  download: async (url: string, filename?: string): Promise<void> => {
    const response = await fetch(config.api.baseUrl + url)
    const blob = await response.blob()
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
