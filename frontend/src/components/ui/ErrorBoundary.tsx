import { Component, ErrorInfo, ReactNode } from 'react'
import { AlertTriangle, RefreshCcw, Home } from 'lucide-react'
import { Button } from './Button'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    }
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)

    this.setState({
      error,
      errorInfo,
    })

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }

    // Log to error reporting service (e.g., Sentry)
    // logErrorToService(error, errorInfo)
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    })
  }

  handleGoHome = () => {
    window.location.href = '/app/dashboard'
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="min-h-screen bg-background flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-card border border-border rounded-2xl shadow-lg p-6">
            {/* Icon */}
            <div className="w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-4" style={{ backgroundColor: 'hsl(var(--destructive) / 0.1)' }}>
              <AlertTriangle className="h-7 w-7" style={{ color: 'hsl(var(--destructive))' }} />
            </div>

            {/* Content */}
            <div className="text-center mb-6">
              <h1 className="text-xl font-bold text-foreground mb-2">
                Algo salió mal
              </h1>
              <p className="text-sm text-muted-foreground">
                Ha ocurrido un error inesperado.
              </p>
            </div>

            {/* Error Details (only in development) */}
            {import.meta.env.DEV && this.state.error && (
              <details className="mb-6 bg-muted border border-border rounded-lg p-3 text-left">
                <summary className="text-xs font-semibold text-foreground mb-2 cursor-pointer hover:text-primary">
                  Detalles del error (solo desarrollo)
                </summary>
                <p className="text-xs font-mono mb-2 mt-2" style={{ color: 'hsl(var(--destructive))' }}>
                  {this.state.error.toString()}
                </p>
                {this.state.errorInfo && (
                  <pre className="text-xs text-muted-foreground whitespace-pre-wrap overflow-auto max-h-40">
                    {this.state.errorInfo.componentStack}
                  </pre>
                )}
              </details>
            )}

            {/* Actions */}
            <div className="flex flex-col gap-2">
              <Button
                onClick={this.handleGoHome}
                className="gap-2 w-full"
              >
                <Home className="h-4 w-4" />
                Ir al Dashboard
              </Button>
              <Button
                onClick={this.handleReset}
                variant="outline"
                className="gap-2 w-full"
              >
                <RefreshCcw className="h-4 w-4" />
                Intentar de nuevo
              </Button>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// Functional wrapper for easier usage
export const withErrorBoundary = <P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryProps?: Omit<Props, 'children'>
) => {
  const WrappedComponent = (props: P) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <Component {...props} />
    </ErrorBoundary>
  )

  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`

  return WrappedComponent
}

export default ErrorBoundary