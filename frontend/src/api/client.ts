import { config } from '@/lib/config'
import { useAuthStore } from '@/store/auth'
import { useAppStore } from '@/store/app'

// Fetch-based API client with request deduplication
class ApiClient {
  private baseURL: string
  private timeout: number
  private pendingRequests = new Map<string, Promise<any>>()
  private requestControllers = new Map<string, AbortController>()

  constructor(baseURL: string, timeout: number) {
    this.baseURL = baseURL
    this.timeout = timeout
  }

  async request<T = unknown>(url: string, options: RequestInit = {}): Promise<T> {
    const requestKey = this.generateRequestKey(url, options)
    
    // Return existing request if pending (deduplication)
    if (this.pendingRequests.has(requestKey)) {
      console.log(`🔄 Deduplicating request: ${requestKey}`)
      return this.pendingRequests.get(requestKey)!
    }

    const controller = new AbortController()
    this.requestControllers.set(requestKey, controller)
    
    const timeoutId = setTimeout(() => {
      console.log(`⏰ Request timeout: ${requestKey}`)
      controller.abort()
    }, this.timeout)

    const requestPromise = this.executeRequest<T>(url, options, controller.signal, timeoutId)
      .finally(() => {
        // Cleanup
        clearTimeout(timeoutId)
        this.pendingRequests.delete(requestKey)
        this.requestControllers.delete(requestKey)
      })

    this.pendingRequests.set(requestKey, requestPromise)
    return requestPromise
  }

  private generateRequestKey(url: string, options: RequestInit): string {
    const method = options.method || 'GET'
    
    // For FormData, create a simple key since we can't stringify it
    let bodyKey = ''
    if (options.body instanceof FormData) {
      bodyKey = 'FormData'
    } else if (options.body) {
      bodyKey = typeof options.body === 'string' ? options.body : JSON.stringify(options.body)
    }
    
    // Include relevant headers in the key (excluding auth token for better deduplication)
    const relevantHeaders = { ...options.headers }
    if (relevantHeaders && typeof relevantHeaders === 'object') {
      delete (relevantHeaders as any)['Authorization']
    }
    
    const headersKey = JSON.stringify(relevantHeaders)
    
    return `${method}:${url}:${bodyKey}:${headersKey}`
  }

  private async executeRequest<T>(
    url: string, 
    options: RequestInit, 
    signal: AbortSignal,
    timeoutId: NodeJS.Timeout
  ): Promise<T> {
    try {
      const token = useAuthStore.getState().token
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...(options.headers as Record<string, string>),
      }

      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }

      // Don't override Content-Type for FormData
      if (options.body instanceof FormData) {
        delete headers['Content-Type']
      }

      const response = await fetch(this.baseURL + url, {
        ...options,
        headers,
        signal,
      })

      if (!response.ok) {
        await this.handleError(response)
      }

      const data = await response.json()
      return data
    } catch (error: unknown) {
      // Handle abort errors gracefully
      if (error instanceof Error && error.name === 'AbortError') {
        console.log(`🚫 Request aborted: ${url}`)
        throw new Error('Request was cancelled')
      }
      throw error
    }
  }

  // Cancel all pending requests (useful for cleanup)
  cancelAllRequests(): void {
    console.log(`🚫 Cancelling ${this.requestControllers.size} pending requests`)
    
    this.requestControllers.forEach((controller, key) => {
      controller.abort()
    })
    
    this.pendingRequests.clear()
    this.requestControllers.clear()
  }

  // Cancel specific request by key
  cancelRequest(url: string, options: RequestInit = {}): boolean {
    const requestKey = this.generateRequestKey(url, options)
    const controller = this.requestControllers.get(requestKey)
    
    if (controller) {
      console.log(`🚫 Cancelling request: ${requestKey}`)
      controller.abort()
      this.pendingRequests.delete(requestKey)
      this.requestControllers.delete(requestKey)
      return true
    }
    
    return false
  }

  // Get pending requests count (useful for debugging)
  getPendingRequestsCount(): number {
    return this.pendingRequests.size
  }

  // Get pending request keys (useful for debugging)
  getPendingRequestKeys(): string[] {
    return Array.from(this.pendingRequests.keys())
  }

  async handleError(response: Response): Promise<never> {
    let errorMessage = 'Error desconocido'

    try {
      const data = await response.json()
      errorMessage = data.message || data.detail || data.error || errorMessage
    } catch {
      errorMessage = response.statusText
    }

    // Handle 401 errors with improved token refresh logic
    if (response.status === 401) {
      const refreshToken = useAuthStore.getState().refreshToken

      if (refreshToken) {
        try {
          // Try to refresh token using the service directly
          // This avoids circular dependencies with React Query hooks
          const { authService } = await import('@/services/authService')
          const refreshResponse = await authService.refreshToken(refreshToken)

          // Update tokens in store
          useAuthStore.getState().setTokens(
            refreshResponse.access_token,
            refreshResponse.refresh_token
          )

          console.log('Token refreshed successfully, user can retry the request')
          // Note: We don't automatically retry here to avoid complexity
          // The calling code should handle retry via React Query's retry mechanism

        } catch (refreshError) {
          console.error('Token refresh failed:', refreshError)

          // Clear auth state and redirect to login
          useAuthStore.getState().logout()

          if (window.location.pathname !== '/login' && window.location.pathname !== '/auth/login') {
            window.location.href = '/auth/login'
          }
        }
      } else {
        // No refresh token available, logout immediately
        useAuthStore.getState().logout()

        if (window.location.pathname !== '/login' && window.location.pathname !== '/auth/login') {
          window.location.href = '/auth/login'
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

  get<T>(url: string, params?: Record<string, string>): Promise<T> {
    const queryString = params ? '?' + new URLSearchParams(params).toString() : ''
    return this.request<T>(url + queryString, { method: 'GET' })
  }

  post<T>(url: string, data?: unknown): Promise<T> {
    return this.request<T>(url, {
      method: 'POST',
      body: data instanceof FormData ? data : JSON.stringify(data),
    })
  }

  put<T>(url: string, data?: unknown): Promise<T> {
    return this.request<T>(url, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  patch<T>(url: string, data?: unknown): Promise<T> {
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

// Cleanup function for when the app unmounts
export const cleanupApiClient = () => {
  apiClient.cancelAllRequests()
}

// Add cleanup on page unload
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', cleanupApiClient)
  window.addEventListener('pagehide', cleanupApiClient)
}

// Type-safe API response wrapper
export interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

// Generic API methods
export const api = {
  get: <T>(url: string, params?: Record<string, string>): Promise<T> => apiClient.get<T>(url, params),
  post: <T>(url: string, data?: unknown): Promise<T> => apiClient.post<T>(url, data),
  put: <T>(url: string, data?: unknown): Promise<T> => apiClient.put<T>(url, data),
  patch: <T>(url: string, data?: unknown): Promise<T> => apiClient.patch<T>(url, data),
  delete: <T>(url: string): Promise<T> => apiClient.delete<T>(url),

  upload: async <T>(url: string, file: File): Promise<T> => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post<T>(url, formData)
  },

  uploadMultiple: async <T>(url: string, files: File[]): Promise<T> => {
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
    }
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

  // Request management utilities
  cancelAllRequests: () => apiClient.cancelAllRequests(),
  cancelRequest: (url: string, options?: RequestInit) => apiClient.cancelRequest(url, options),
  getPendingRequestsCount: () => apiClient.getPendingRequestsCount(),
  getPendingRequestKeys: () => apiClient.getPendingRequestKeys(),
}

export default api
