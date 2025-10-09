import { useEffect, lazy, Suspense } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { Toaster } from 'sonner'
import { useAuthStore } from '@/store/auth'
import { useAppStore } from '@/store/app'
import { routes, env } from '@/lib/config'

// Layouts (eager load)
import PublicLayout from '@/components/layouts/PublicLayout'
import AppLayout from '@/components/layouts/AppLayout'
import AuthLayoutWrapper from '@/components/layouts/AuthLayoutWrapper'

// Components (eager load)
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import ErrorBoundary from '@/components/ui/ErrorBoundary'

// Public Pages (eager load for better UX)
import HomePage from '@/pages/public/HomePage'
import LoginPage from '@/pages/public/LoginPage'
import RegisterPage from '@/pages/public/RegisterPage'

// Lazy load other public pages
const ReportPage = lazy(() => import('@/pages/public/ReportPage'))
const AboutPage = lazy(() => import('@/pages/public/AboutPage'))
const ContactPage = lazy(() => import('@/pages/public/ContactPage'))

// Lazy load app pages
const DashboardPage = lazy(() => import('@/pages/app/DashboardPage'))
const AnalysisPage = lazy(() => import('@/pages/app/AnalysisPage'))
const AnalysisDetailPage = lazy(() => import('@/pages/app/AnalysisDetailPage'))
const UploadsPage = lazy(() => import('@/pages/app/UploadsPage'))
const ReportsPage = lazy(() => import('@/pages/app/ReportsPage'))
const UsersPage = lazy(() => import('@/pages/app/UsersPage'))
const SettingsPage = lazy(() => import('@/pages/app/SettingsPage'))
const ProfilePage = lazy(() => import('@/pages/app/ProfilePage'))

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
            useAppStore.getState().addNotification({
              type: 'error',
              title: 'Error del servidor',
              message: 'Ha ocurrido un error en el servidor. Por favor, intenta nuevamente.',
              duration: 10000,
            })
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
  const isAuthenticated = useAuthStore(state => !!state.token && !!state.user)
  const isLoading = useAuthStore(state => state.isLoading)
  const user = useAuthStore(state => state.user)

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-sm text-gray-600">Cargando...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to={routes.public.login} replace />
  }

  // Role-based access control
  if (allowedRoles && allowedRoles.length > 0) {
    const hasAccess = user?.role && allowedRoles.includes(user.role)
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
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (isAuthenticated) {
    return <Navigate to={routes.app.dashboard} replace />
  }

  return <>{children}</>
}

// Loading fallback component
const PageLoader = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50">
    <div className="text-center">
      <LoadingSpinner size="lg" />
      <p className="mt-4 text-sm text-gray-600">Cargando página...</p>
    </div>
  </div>
)

function App() {
  const initializeAuth = useAuthStore(state => state.initializeAuth)

  useEffect(() => {
    initializeAuth()
  }, [initializeAuth])

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <Router>
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
                <Route
                  path={routes.public.about}
                  element={
                    <PublicLayout>
                      <AboutPage />
                    </PublicLayout>
                  }
                />
                <Route
                  path={routes.public.contact}
                  element={
                    <PublicLayout>
                      <ContactPage />
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
              <Route
                path={routes.app.uploads}
                element={
                  <ProtectedRoute>
                    <AppLayout>
                      <UploadsPage />
                    </AppLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path={routes.app.reports}
                element={
                  <ProtectedRoute>
                    <AppLayout>
                      <ReportsPage />
                    </AppLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path={routes.app.users}
                element={
                  <ProtectedRoute allowedRoles={['ADMIN', 'EXPERT']}>
                    <AppLayout>
                      <UsersPage />
                    </AppLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path={routes.app.settings}
                element={
                  <ProtectedRoute>
                    <AppLayout>
                      <SettingsPage />
                    </AppLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path={routes.app.profile}
                element={
                  <ProtectedRoute>
                    <AppLayout>
                      <ProfilePage />
                    </AppLayout>
                  </ProtectedRoute>
                }
              />

                {/* Catch all route */}
                <Route path="*" element={<Navigate to={routes.public.home} replace />} />
              </Routes>
            </Suspense>
          </div>

          {/* Global Toast Notifications */}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 5000,
              className: 'sentrix-toast',
            }}
          />
        </Router>

        {/* React Query Devtools (only in development) */}
        {env.isDev && <ReactQueryDevtools initialIsOpen={false} />}
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App