import { Component, ErrorInfo, ReactNode } from 'react'
import { AlertTriangle, RefreshCcw, Home, Wifi, WifiOff } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from './Button'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
  showToast?: boolean
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
  isNetworkError: boolean
  isRetrying: boolean
}

interface ApiError extends Error {
  status?: number
  code?: string
  details?: unknown
}

class ApiErrorBoundary extends Component<Props, State> {
  private retryTimeoutId: NodeJS.Timeout | null = null

  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      isNetworkError: false,
      isRetrying: false,
    }
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    const isNetworkError = ApiErrorBoundary.isNetworkError(error)
    return { 
      hasError: true,
      isNetworkError,
    }
  }

  static isNetworkError(error: Error): boolean {
    return (
      error.name === 'NetworkError' ||
      error.message.includes('fetch') ||
      error.message.includes('network') ||
      error.message.includes('Failed to fetch') ||
      error.message.includes('ERR_NETWORK') ||
      error.message.includes('ERR_INTERNET_DISCONNECTED')
    )
  }

  static isApiError(error: Error): error is ApiError {
    return 'status' in error || 'code' in error
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ApiErrorBoundary caught an error:', error, errorInfo)

    this.setState({
      error,
      errorInfo,
    })

    // Log error details for debugging
    this.logError(error, errorInfo)

    // Show toast notification if enabled
    if (this.props.showToast !== false) {
      this.showErrorToast(error)
    }

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }
  }

  private logError(error: Error, errorInfo: ErrorInfo) {
    const errorDetails = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
    }

    // In production, send to error reporting service
    if (process.env.NODE_ENV === 'production') {
      // Example: Send to Sentry, LogRocket, etc.
      console.error('API Error Details:', errorDetails)
    } else {
      console.group('🚨 API Error Details')
      console.error('Error:', error)
      console.error('Error Info:', errorInfo)
      console.error('Full Details:', errorDetails)
      console.groupEnd()
    }
  }

  private showErrorToast(error: Error) {
    const isApiError = ApiErrorBoundary.isApiError(error)
    const isNetworkError = ApiErrorBoundary.isNetworkError(error)

    if (isNetworkError) {
      toast.error('Error de conexión', {
        description: 'Verifica tu conexión a internet e intenta nuevamente.',
        action: {
          label: 'Reintentar',
          onClick: () => this.handleRetry(),
        },
      })
    } else if (isApiError && error.status) {
      if (error.status >= 500) {
        toast.error('Error del servidor', {
          description: 'Ha ocurrido un error en el servidor. Nuestro equipo ha sido notificado.',
        })
      } else if (error.status === 401) {
        toast.error('Sesión expirada', {
          description: 'Tu sesión ha expirado. Por favor, inicia sesión nuevamente.',
        })
      } else if (error.status === 403) {
        toast.error('Acceso denegado', {
          description: 'No tienes permisos para realizar esta acción.',
        })
      } else {
        toast.error('Error en la solicitud', {
          description: error.message || 'Ha ocurrido un error inesperado.',
        })
      }
    } else {
      toast.error('Error inesperado', {
        description: 'Ha ocurrido un error inesperado. Por favor, intenta nuevamente.',
      })
    }
  }

  handleReset = () => {
    if (this.retryTimeoutId) {
      clearTimeout(this.retryTimeoutId)
      this.retryTimeoutId = null
    }

    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      isNetworkError: false,
      isRetrying: false,
    })
  }

  handleRetry = () => {
    this.setState({ isRetrying: true })
    
    // Add a small delay to show the retrying state
    this.retryTimeoutId = setTimeout(() => {
      this.handleReset()
    }, 1000)
  }

  handleGoHome = () => {
    window.location.href = '/app/dashboard'
  }

  handleReload = () => {
    window.location.reload()
  }

  componentWillUnmount() {
    if (this.retryTimeoutId) {
      clearTimeout(this.retryTimeoutId)
    }
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      const { error, isNetworkError, isRetrying } = this.state
      const isApiError = error && ApiErrorBoundary.isApiError(error)

      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <div className="max-w-2xl w-full bg-white rounded-lg shadow-lg p-8">
            {/* Icon */}
            <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 ${
              isNetworkError 
                ? 'bg-orange-100' 
                : isApiError && error.status && error.status >= 500
                ? 'bg-red-100'
                : 'bg-yellow-100'
            }`}>
              {isNetworkError ? (
                <WifiOff className={`h-8 w-8 ${
                  isNetworkError ? 'text-orange-600' : 'text-red-600'
                }`} />
              ) : (
                <AlertTriangle className={`h-8 w-8 ${
                  isApiError && error.status && error.status >= 500
                    ? 'text-red-600'
                    : 'text-yellow-600'
                }`} />
              )}
            </div>

            {/* Content */}
            <div className="text-center mb-8">
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                {isNetworkError 
                  ? 'Error de conexión'
                  : isApiError && error.status === 401
                  ? 'Sesión expirada'
                  : isApiError && error.status === 403
                  ? 'Acceso denegado'
                  : isApiError && error.status && error.status >= 500
                  ? 'Error del servidor'
                  : 'Algo salió mal'
                }
              </h1>
              <p className="text-base text-gray-600">
                {isNetworkError 
                  ? 'No se pudo conectar con el servidor. Verifica tu conexión a internet.'
                  : isApiError && error.status === 401
                  ? 'Tu sesión ha expirado. Por favor, inicia sesión nuevamente.'
                  : isApiError && error.status === 403
                  ? 'No tienes permisos para acceder a este recurso.'
                  : isApiError && error.status && error.status >= 500
                  ? 'Ha ocurrido un error en el servidor. Nuestro equipo ha sido notificado.'
                  : 'Ha ocurrido un error inesperado. Por favor, intenta nuevamente.'
                }
              </p>
            </div>

            {/* Error Details (only in development) */}
            {process.env.NODE_ENV === 'development' && error && (
              <div className="mb-6 bg-gray-50 border border-gray-200 rounded-lg p-4 overflow-auto">
                <h3 className="text-sm font-semibold text-gray-900 mb-2">
                  Error Details (Development Only)
                </h3>
                <p className="text-xs text-red-600 font-mono mb-2">
                  {error.toString()}
                </p>
                {isApiError && error.status && (
                  <p className="text-xs text-blue-600 font-mono mb-2">
                    Status: {error.status}
                  </p>
                )}
                {this.state.errorInfo && (
                  <pre className="text-xs text-gray-700 whitespace-pre-wrap max-h-32 overflow-y-auto">
                    {this.state.errorInfo.componentStack}
                  </pre>
                )}
              </div>
            )}

            {/* Actions */}
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              {isNetworkError ? (
                <>
                  <Button
                    onClick={this.handleRetry}
                    disabled={isRetrying}
                    variant="outline"
                    className="gap-2"
                  >
                    <Wifi className="h-4 w-4" />
                    {isRetrying ? 'Reintentando...' : 'Reintentar conexión'}
                  </Button>
                  <Button
                    onClick={this.handleReload}
                    className="gap-2 bg-gradient-to-r from-primary-600 to-cyan-600"
                  >
                    <RefreshCcw className="h-4 w-4" />
                    Recargar página
                  </Button>
                </>
              ) : isApiError && error.status === 401 ? (
                <Button
                  onClick={() => window.location.href = '/auth/login'}
                  className="gap-2 bg-gradient-to-r from-primary-600 to-cyan-600"
                >
                  Iniciar sesión
                </Button>
              ) : (
                <>
                  <Button
                    onClick={this.handleReset}
                    disabled={isRetrying}
                    variant="outline"
                    className="gap-2"
                  >
                    <RefreshCcw className="h-4 w-4" />
                    {isRetrying ? 'Reintentando...' : 'Intentar de nuevo'}
                  </Button>
                  <Button
                    onClick={this.handleGoHome}
                    className="gap-2 bg-gradient-to-r from-primary-600 to-cyan-600"
                  >
                    <Home className="h-4 w-4" />
                    Ir al Dashboard
                  </Button>
                </>
              )}
            </div>

            {/* Support Info */}
            <div className="mt-8 pt-6 border-t border-gray-200 text-center">
              <p className="text-sm text-gray-600">
                Si el problema persiste, contacta a{' '}
                <a
                  href="mailto:contact@sentrix.ar"
                  className="text-primary-600 hover:underline font-medium"
                >
                  contact@sentrix.ar
                </a>
              </p>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// Functional wrapper for easier usage with API operations
export const withApiErrorBoundary = <P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryProps?: Omit<Props, 'children'>
) => {
  const WrappedComponent = (props: P) => (
    <ApiErrorBoundary {...errorBoundaryProps}>
      <Component {...props} />
    </ApiErrorBoundary>
  )

  WrappedComponent.displayName = `withApiErrorBoundary(${Component.displayName || Component.name})`

  return WrappedComponent
}

export default ApiErrorBoundary