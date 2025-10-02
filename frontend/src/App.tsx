import { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { Toaster } from 'sonner'
import { useAuthStore } from '@/store/auth'
import { routes, env } from '@/lib/config'

// Layouts
import PublicLayout from '@/components/layouts/PublicLayout'
import AppLayout from '@/components/layouts/AppLayout'

// Public Pages
import HomePage from '@/pages/public/HomePage'
import ReportPage from '@/pages/public/ReportPage'
import AboutPage from '@/pages/public/AboutPage'
import ContactPage from '@/pages/public/ContactPage'
import LoginPage from '@/pages/public/LoginPage'
import RegisterPage from '@/pages/public/RegisterPage'

// App Pages (Private)
import DashboardPage from '@/pages/app/DashboardPage'
import AnalysisPage from '@/pages/app/AnalysisPage'
import AnalysisDetailPage from '@/pages/app/AnalysisDetailPage'
import UploadsPage from '@/pages/app/UploadsPage'
import ReportsPage from '@/pages/app/ReportsPage'
import UsersPage from '@/pages/app/UsersPage'
import SettingsPage from '@/pages/app/SettingsPage'
import ProfilePage from '@/pages/app/ProfilePage'

// Components
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import ErrorBoundary from '@/components/ui/ErrorBoundary'

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: (failureCount, error: any) => {
        if (error?.status === 401) return false
        return failureCount < 3
      },
    },
    mutations: {
      retry: false,
    },
  },
})

// Protected Route Component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore(state => !!state.token && !!state.user)
  const isLoading = useAuthStore(state => state.isLoading)

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to={routes.public.login} replace />
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
              <Route
                path={routes.public.login}
                element={
                  <PublicRoute>
                    <LoginPage />
                  </PublicRoute>
                }
              />
              <Route
                path={routes.public.register}
                element={
                  <PublicRoute>
                    <RegisterPage />
                  </PublicRoute>
                }
              />

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
                  <ProtectedRoute>
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