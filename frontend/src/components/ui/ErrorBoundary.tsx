import { Component, ErrorInfo, ReactNode } from 'react'
import { Button } from './Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './Card'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
  errorInfo?: ErrorInfo
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
    this.setState({ error, errorInfo })

    // Here you could send error to monitoring service
    // sendErrorToMonitoring(error, errorInfo)
  }

  handleReload = () => {
    window.location.reload()
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="min-h-screen flex items-center justify-center p-4 bg-background">
          <Card className="w-full max-w-md">
            <CardHeader className="text-center">
              <div className="mx-auto mb-4 h-12 w-12 rounded-full bg-destructive/10 flex items-center justify-center">
                <svg
                  className="h-6 w-6 text-destructive"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
                  />
                </svg>
              </div>
              <CardTitle className="text-destructive">¡Algo salió mal!</CardTitle>
              <CardDescription>
                Ha ocurrido un error inesperado en la aplicación. Puedes intentar recargar la página o reportar el problema.
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-4">
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <details className="rounded-md bg-muted p-4 text-sm">
                  <summary className="cursor-pointer font-medium">
                    Detalles del error (desarrollo)
                  </summary>
                  <div className="mt-2 space-y-2">
                    <p className="font-medium">Error:</p>
                    <pre className="whitespace-pre-wrap text-xs">
                      {this.state.error.message}
                    </pre>
                    <p className="font-medium">Stack trace:</p>
                    <pre className="whitespace-pre-wrap text-xs">
                      {this.state.error.stack}
                    </pre>
                    {this.state.errorInfo && (
                      <>
                        <p className="font-medium">Component stack:</p>
                        <pre className="whitespace-pre-wrap text-xs">
                          {this.state.errorInfo.componentStack}
                        </pre>
                      </>
                    )}
                  </div>
                </details>
              )}

              <div className="flex flex-col space-y-2">
                <Button onClick={this.handleReload} className="w-full">
                  Recargar página
                </Button>
                <Button
                  onClick={this.handleReset}
                  variant="outline"
                  className="w-full"
                >
                  Intentar nuevamente
                </Button>
              </div>

              <div className="text-center text-sm text-muted-foreground">
                <p>
                  Si el problema persiste, contacta al{' '}
                  <a
                    href="mailto:soporte@sentrix.com"
                    className="text-primary hover:underline"
                  >
                    soporte técnico
                  </a>
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary