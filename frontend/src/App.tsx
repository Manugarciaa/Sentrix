import { useEffect, lazy, Suspense } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { Toaster } from '@/components/ui/sonner'
import { useAuthStore } from '@/store/auth'
import { showToast } from '@/lib/toast'
import { routes, env } from '@/lib/config'

// Layouts (eager load)
import PublicLayout from '@/components/layouts/PublicLayout'
import AppLayout from '@/components/layouts/AppLayout'
import AuthLayoutWrapper from '@/components/layouts/AuthLayoutWrapper'

// Components (eager load)
import ErrorBoundary from '@/components/ui/ErrorBoundary'
import ScrollToTop from '@/components/ui/ScrollToTop'

// Public Pages (eager load for better UX)
import HomePage from '@/pages/public/HomePage'
import LoginPage from '@/pages/public/LoginPage'
import RegisterPage from '@/pages/public/RegisterPage'

// Lazy load other public pages
const ReportPage = lazy(() => import('@/pages/public/ReportPage'))
const NotFoundPage = lazy(() => import('@/pages/NotFoundPage'))

// Lazy load app pages
const DashboardPage = lazy(() => import('@/pages/app/DashboardPage'))
const AnalysisPage = lazy(() => import('@/pages/app/AnalysisPage'))
const AnalysisDetailPage = lazy(() => import('@/pages/app/AnalysisDetailPage'))

// Create a client with enhanced configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
      retry: (failureCount, error: unknown) => {
        // Don't retry on authentication or authorization errors
        if (error && typeof error === 'object' && 'status' in error) {
          const status = error.status as number
          if (status === 401 || status === 403) return false
        }
        // Don't retry on client errors (4xx except 401/403)
        if (error && typeof error === 'object' && 'status' in error) {
          const status = error.status as number
          if (status >= 400 && status < 500 && status !== 401 && status !== 403) return false
        }
        return failureCount < 3
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
      refetchOnMount: true,
    },
    mutations: {
      retry: false,
      onError: (error: unknown) => {
        // Global mutation error handling
        console.error('Mutation error:', error)
        
        // Handle specific error types
        if (error && typeof error === 'object' && 'status' in error) {
          const status = error.status as number
          if (status === 401) {
            // Handle auth errors - will be handled by individual mutations
            return
          } else if (status >= 500) {
            // Handle server errors
            showToast.error(
              'Error del servidor',
              'Ha ocurrido un error en el servidor. Por favor, intenta nuevamente.',
              { duration: 10000 }
            )
          }
        }
      },
      onSuccess: () => {
        // Global success handling if needed
        console.log('Mutation completed successfully')
      },
    },
  },
})

// Protected Route Component with Role-Based Access
interface ProtectedRouteProps {
  children: React.ReactNode
  allowedRoles?: string[]
}

function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const token = useAuthStore(state => state.token)
  const user = useAuthStore(state => state.user)
  const isLoading = useAuthStore(state => state.isLoading)

  // If still checking auth (initial load), show loading
  if (isLoading) {
    return <>{children}</>
  }

  // No token = not authenticated
  if (!token) {
    // Save the current location to return after login
    const currentPath = window.location.pathname
    return <Navigate to={routes.public.login} state={{ from: currentPath }} replace />
  }

  // Token exists but user not loaded yet - allow render with skeleton
  // This happens briefly during session restoration
  if (!user) {
    return <>{children}</>
  }

  // Role-based access control (only after user is loaded)
  if (allowedRoles && allowedRoles.length > 0) {
    const hasAccess = user.role && allowedRoles.includes(user.role)
    if (!hasAccess) {
      return <Navigate to={routes.app.dashboard} replace />
    }
  }

  return <>{children}</>
}

// Public Route Component (redirect if authenticated)
function PublicRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore(state => !!state.token && !!state.user)
  const isLoading = useAuthStore(state => state.isLoading)

  if (isLoading) {
    return <div className="min-h-screen bg-background" />
  }

  if (isAuthenticated) {
    // Check if there's a return path from login attempt
    const returnPath = (window.history.state && window.history.state.usr?.from) || routes.app.dashboard
    return <Navigate to={returnPath} replace />
  }

  return <>{children}</>
}

// Loading fallback component - Minimal loader for route transitions
const PageLoader = () => (
  <div className="min-h-screen bg-background" />
)

function App() {
  const initializeAuth = useAuthStore(state => state.initializeAuth)

  useEffect(() => {
    initializeAuth()
    // Empty deps array - only run once on mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        {/* Global Toast Notifications - Sonner from shadcn/ui */}
        <Toaster />

        <Router
          future={{
            v7_startTransition: true,
            v7_relativeSplatPath: true,
          }}
        >
          <ScrollToTop />
          <div className="min-h-screen bg-background">
            <Suspense fallback={<PageLoader />}>
              <Routes>
                {/* Public Routes */}
                <Route
                  path={routes.public.home}
                  element={
                    <PublicLayout>
                      <HomePage />
                    </PublicLayout>
                  }
                />
                <Route
                  path={routes.public.report}
                  element={
                    <PublicLayout>
                      <ReportPage />
                    </PublicLayout>
                  }
                />

              {/* Auth Routes */}
              <Route path="/auth" element={<AuthLayoutWrapper />}>
                <Route
                  path="login"
                  element={
                    <PublicRoute>
                      <LoginPage />
                    </PublicRoute>
                  }
                />
                <Route
                  path="register"
                  element={
                    <PublicRoute>
                      <RegisterPage />
                    </PublicRoute>
                  }
                />
              </Route>

              {/* Protected App Routes */}
              <Route
                path={routes.app.dashboard}
                element={
                  <ProtectedRoute>
                    <AppLayout>
                      <DashboardPage />
                    </AppLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path={routes.app.analysis}
                element={
                  <ProtectedRoute>
                    <AppLayout>
                      <AnalysisPage />
                    </AppLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/app/analysis/:id"
                element={
                  <ProtectedRoute>
                    <AppLayout>
                      <AnalysisDetailPage />
                    </AppLayout>
                  </ProtectedRoute>
                }
              />

                {/* Catch all route - 404 */}
                <Route path="*" element={<NotFoundPage />} />
              </Routes>
            </Suspense>
          </div>
        </Router>

        {/* React Query Devtools (only in development) */}
        {env.isDev && <ReactQueryDevtools initialIsOpen={false} />}
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App