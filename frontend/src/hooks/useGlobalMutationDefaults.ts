import { MutationOptions } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/auth'
import { useAppStore } from '@/store/app'
import { authService } from '@/services/authService'

/**
 * API Error interface for consistent error handling
 */
export interface ApiError extends Error {
  status?: number
  code?: string
  details?: Record<string, any>
  field?: string
}

/**
 * Error type classification for different handling strategies
 */
export enum ErrorType {
  NETWORK = 'network',
  AUTHENTICATION = 'authentication',
  AUTHORIZATION = 'authorization',
  VALIDATION = 'validation',
  SERVER = 'server',
  CLIENT = 'client',
  TIMEOUT = 'timeout',
  UNKNOWN = 'unknown'
}

/**
 * Classify error based on status code and message
 */
export const classifyError = (error: any): ErrorType => {
  if (!error) return ErrorType.UNKNOWN

  // Network errors
  if (error.name === 'AbortError' || error.message?.includes('cancelled')) {
    return ErrorType.TIMEOUT
  }
  
  if (error.message?.includes('Failed to fetch') || error.message?.includes('Network')) {
    return ErrorType.NETWORK
  }

  // HTTP status-based classification
  if (error.status) {
    if (error.status === 401) return ErrorType.AUTHENTICATION
    if (error.status === 403) return ErrorType.AUTHORIZATION
    if (error.status >= 400 && error.status < 500) return ErrorType.VALIDATION
    if (error.status >= 500) return ErrorType.SERVER
  }

  return ErrorType.UNKNOWN
}

/**
 * Get user-friendly error messages based on error type and context
 */
export const getErrorMessage = (error: any, context?: string): string => {
  const errorType = classifyError(error)
  
  // Use server-provided message if available and user-friendly
  const serverMessage = error?.message || error?.detail || error?.error
  
  switch (errorType) {
    case ErrorType.NETWORK:
      return 'No se pudo conectar con el servidor. Verifica tu conexión a internet.'
    
    case ErrorType.AUTHENTICATION:
      return 'Tu sesión ha expirado. Por favor, inicia sesión nuevamente.'
    
    case ErrorType.AUTHORIZATION:
      return 'No tienes permisos para realizar esta acción.'
    
    case ErrorType.VALIDATION:
      // For validation errors, prefer server message as it's usually specific
      if (serverMessage && serverMessage.length < 200) {
        return serverMessage
      }
      return context ? `Error de validación en ${context}` : 'Los datos proporcionados no son válidos.'
    
    case ErrorType.SERVER:
      return 'Error interno del servidor. Por favor, intenta nuevamente en unos momentos.'
    
    case ErrorType.TIMEOUT:
      return 'La operación fue cancelada o tardó demasiado tiempo.'
    
    case ErrorType.CLIENT:
      return serverMessage || 'Ha ocurrido un error en la aplicación.'
    
    default:
      return serverMessage || 'Ha ocurrido un error inesperado.'
  }
}

/**
 * Get error title based on error type
 */
export const getErrorTitle = (error: any, context?: string): string => {
  const errorType = classifyError(error)
  
  switch (errorType) {
    case ErrorType.NETWORK:
      return 'Error de conexión'
    
    case ErrorType.AUTHENTICATION:
      return 'Sesión expirada'
    
    case ErrorType.AUTHORIZATION:
      return 'Acceso denegado'
    
    case ErrorType.VALIDATION:
      return context ? `Error en ${context}` : 'Error de validación'
    
    case ErrorType.SERVER:
      return 'Error del servidor'
    
    case ErrorType.TIMEOUT:
      return 'Operación cancelada'
    
    default:
      return 'Error'
  }
}

/**
 * Handle automatic token refresh on 401 errors
 */
export const handleTokenRefresh = async (): Promise<boolean> => {
  const { refreshToken, setTokens, logout } = useAuthStore.getState()
  
  if (!refreshToken) {
    console.warn('No refresh token available for automatic refresh')
    return false
  }

  try {
    console.log('🔄 Attempting automatic token refresh...')
    const response = await authService.refreshToken(refreshToken)
    
    // Update tokens in store
    setTokens(response.access_token, response.refresh_token)
    
    console.log('[OK] Token refresh successful')
    return true
    
  } catch (refreshError) {
    console.error('[ERROR] Token refresh failed:', refreshError)
    
    // Clear auth state and redirect to login
    logout()
    
    // Show notification
    useAppStore.getState().addNotification({
      type: 'error',
      title: 'Sesión expirada',
      message: 'Tu sesión ha expirado. Por favor, inicia sesión nuevamente.',
      duration: 5000,
    })
    
    // Redirect to login if not already there
    if (window.location.pathname !== '/auth/login') {
      window.location.href = '/auth/login'
    }
    
    return false
  }
}

/**
 * Global mutation error handler with automatic token refresh
 */
export const createGlobalMutationErrorHandler = (context?: string) => {
  return async (error: any) => {
    console.error(`🚨 Mutation error${context ? ` in ${context}` : ''}:`, error)
    
    const errorType = classifyError(error)
    
    // Handle authentication errors with automatic token refresh
    if (errorType === ErrorType.AUTHENTICATION) {
      const refreshSuccess = await handleTokenRefresh()
      
      if (refreshSuccess) {
        // Don't show error notification if refresh was successful
        // The mutation will be retried automatically by React Query
        return
      }
      
      // If refresh failed, the handleTokenRefresh function already handled logout and notification
      return
    }
    
    // Handle authorization errors
    if (errorType === ErrorType.AUTHORIZATION) {
      useAppStore.getState().addNotification({
        type: 'error',
        title: getErrorTitle(error, context),
        message: getErrorMessage(error, context),
        duration: 5000,
      })
      return
    }
    
    // Handle network errors
    if (errorType === ErrorType.NETWORK) {
      useAppStore.getState().addNotification({
        type: 'warning',
        title: getErrorTitle(error, context),
        message: getErrorMessage(error, context),
        duration: 7000,
      })
      return
    }
    
    // Handle server errors
    if (errorType === ErrorType.SERVER) {
      useAppStore.getState().addNotification({
        type: 'error',
        title: getErrorTitle(error, context),
        message: getErrorMessage(error, context),
        duration: 8000,
      })
      return
    }
    
    // Handle validation errors
    if (errorType === ErrorType.VALIDATION) {
      useAppStore.getState().addNotification({
        type: 'error',
        title: getErrorTitle(error, context),
        message: getErrorMessage(error, context),
        duration: 6000,
      })
      return
    }
    
    // Handle timeout/cancellation errors (usually don't need user notification)
    if (errorType === ErrorType.TIMEOUT) {
      console.log('Request was cancelled or timed out - no user notification needed')
      return
    }
    
    // Handle unknown errors
    useAppStore.getState().addNotification({
      type: 'error',
      title: getErrorTitle(error, context),
      message: getErrorMessage(error, context),
      duration: 5000,
    })
  }
}

/**
 * Global mutation success handler for consistent success feedback
 */
export const createGlobalMutationSuccessHandler = (
  context?: string,
  customMessage?: string
) => {
  return (data: any) => {
    if (customMessage) {
      useAppStore.getState().addNotification({
        type: 'success',
        title: 'Operación exitosa',
        message: customMessage,
        duration: 3000,
      })
    }
    
    console.log(`[OK] Mutation success${context ? ` in ${context}` : ''}:`, data)
  }
}

/**
 * Hook that provides global mutation defaults with consistent error handling
 */
export const useGlobalMutationDefaults = <TData = unknown, TError = unknown, TVariables = unknown>(
  context?: string,
  options?: {
    showSuccessNotification?: boolean
    successMessage?: string
    enableAutoRetry?: boolean
    retryCondition?: (error: any) => boolean
  }
): Partial<MutationOptions<TData, TError, TVariables>> => {
  
  return {
    // Global error handler
    onError: createGlobalMutationErrorHandler(context),
    
    // Global success handler (optional)
    onSuccess: options?.showSuccessNotification 
      ? createGlobalMutationSuccessHandler(context, options.successMessage)
      : undefined,
    
    // Retry configuration
    retry: options?.enableAutoRetry ? (failureCount: number, error: any) => {
      // Don't retry validation errors or authorization errors
      const errorType = classifyError(error)
      if (errorType === ErrorType.VALIDATION || errorType === ErrorType.AUTHORIZATION) {
        return false
      }
      
      // Custom retry condition
      if (options.retryCondition && !options.retryCondition(error)) {
        return false
      }
      
      // Retry network and server errors up to 2 times
      if (errorType === ErrorType.NETWORK || errorType === ErrorType.SERVER) {
        return failureCount < 2
      }
      
      // Don't retry authentication errors (handled by token refresh)
      if (errorType === ErrorType.AUTHENTICATION) {
        return false
      }
      
      return false
    } : false,
    
    // Retry delay with exponential backoff
    retryDelay: (attemptIndex: number) => Math.min(1000 * 2 ** attemptIndex, 30000),
  }
}

/**
 * Hook for mutations that require authentication
 * Automatically handles token refresh on 401 errors
 */
export const useAuthenticatedMutationDefaults = <TData = unknown, TError = unknown, TVariables = unknown>(
  context?: string,
  options?: {
    showSuccessNotification?: boolean
    successMessage?: string
  }
): Partial<MutationOptions<TData, TError, TVariables>> => {
  
  return {
    ...useGlobalMutationDefaults(context, {
      ...options,
      enableAutoRetry: true,
      retryCondition: (error: any) => {
        // Retry authentication errors after token refresh
        const errorType = classifyError(error)
        return errorType === ErrorType.AUTHENTICATION
      }
    }),
    
    // Custom retry logic for authentication
    retry: (failureCount: number, error: any) => {
      const errorType = classifyError(error)
      
      // For authentication errors, allow one retry after token refresh
      if (errorType === ErrorType.AUTHENTICATION && failureCount === 0) {
        return true
      }
      
      // For network/server errors, allow up to 2 retries
      if ((errorType === ErrorType.NETWORK || errorType === ErrorType.SERVER) && failureCount < 2) {
        return true
      }
      
      return false
    },
  }
}

/**
 * Utility function to create mutation options with global defaults
 */
export const createMutationOptions = <TData = unknown, TError = unknown, TVariables = unknown>(
  mutationFn: (variables: TVariables) => Promise<TData>,
  context?: string,
  options?: {
    showSuccessNotification?: boolean
    successMessage?: string
    enableAutoRetry?: boolean
    requiresAuth?: boolean
    onSuccess?: (data: TData, variables: TVariables) => void
    onError?: (error: TError, variables: TVariables) => void
  }
): MutationOptions<TData, TError, TVariables> => {
  
  const globalDefaults = options?.requiresAuth 
    ? useAuthenticatedMutationDefaults(context, options)
    : useGlobalMutationDefaults(context, options)
  
  return {
    mutationFn,
    ...globalDefaults,
    
    // Combine global and custom handlers
    onSuccess: (data: TData, variables: TVariables, context: unknown) => {
      // Call global success handler first
      if (globalDefaults.onSuccess) {
        globalDefaults.onSuccess(data, variables, context)
      }
      
      // Then call custom success handler
      if (options?.onSuccess) {
        options.onSuccess(data, variables)
      }
    },
    
    onError: (error: TError, variables: TVariables, context: unknown) => {
      // Call global error handler first
      if (globalDefaults.onError) {
        globalDefaults.onError(error, variables, context)
      }
      
      // Then call custom error handler
      if (options?.onError) {
        options.onError(error, variables)
      }
    },
  }
}

export default useGlobalMutationDefaults