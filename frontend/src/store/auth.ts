import { create } from 'zustand'
import type { User, AuthState } from '@/types'
import { config } from '@/lib/config'

/**
 * Auth Store - Migrated to work with React Query
 * 
 * MIGRATION GUIDE:
 * ================
 * 
 * OLD WAY (deprecated):
 * ```typescript
 * const { login, register, refreshTokenAction } = useAuthStore()
 * await login(email, password)
 * ```
 * 
 * NEW WAY (recommended):
 * ```typescript
 * import { useLogin, useRegister, useRefreshToken } from '@/hooks/useAuthMutations'
 * 
 * const loginMutation = useLogin()
 * loginMutation.mutate({ email, password })
 * ```
 * 
 * BENEFITS OF NEW APPROACH:
 * - Better error handling and loading states
 * - Automatic retry logic
 * - Optimistic updates for profile changes
 * - Request deduplication
 * - Better integration with React Query cache
 * 
 * BACKWARD COMPATIBILITY:
 * The old methods are still available but will show deprecation warnings.
 * They will be removed in a future version.
 */

interface AuthStore extends AuthState {
  // Actions - now primarily for state management, not API calls
  logout: () => void
  updateUser: (userData: Partial<User>) => void
  setUser: (user: User) => void
  initializeAuth: () => void
  clearError: () => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setTokens: (token: string, refreshToken: string) => void

  // Deprecated actions - kept for backward compatibility
  // These will be removed in a future version
  // Use React Query hooks instead: useLogin, useRegister, useRefreshToken
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name: string) => Promise<void>
  refreshTokenAction: () => Promise<void>
}

// Guard to prevent multiple simultaneous initializations
let isInitializing = false

export const useAuthStore = create<AuthStore>()((set, get) => ({
      // Initial state
      user: null,
      token: null,
      refreshToken: null,
      isLoading: true, // Start as true to prevent premature redirects on app load
      error: null,

      // Primary actions - for state management
      logout: () => {
        // Clear tokens from localStorage
        localStorage.removeItem(config.auth.tokenKey)
        localStorage.removeItem(config.auth.refreshTokenKey)

        // Reset state
        set({
          user: null,
          token: null,
          refreshToken: null,
          isLoading: false,
          error: null,
        })
      },

      updateUser: (userData: Partial<User>) => {
        const { user } = get()
        if (user) {
          set({
            user: { ...user, ...userData }
          })
        }
      },

      setUser: (user: User) => {
        set({ user })
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading })
      },

      setError: (error: string | null) => {
        set({ error })
      },

      setTokens: (token: string, refreshToken: string) => {
        set({ token, refreshToken })
        
        // Store tokens in localStorage
        localStorage.setItem(config.auth.tokenKey, token)
        localStorage.setItem(config.auth.refreshTokenKey, refreshToken)
      },

      clearError: () => {
        set({ error: null })
      },

      initializeAuth: async () => {
        // Prevent multiple simultaneous initializations
        if (isInitializing) {
          if (import.meta.env.DEV) {
            console.log('Auth initialization already in progress, skipping...')
          }
          return
        }

        isInitializing = true

        try {
          const token = localStorage.getItem(config.auth.tokenKey)
          const refreshToken = localStorage.getItem(config.auth.refreshTokenKey)

          // If no tokens, just set loading to false
          if (!token || !refreshToken) {
            set({ isLoading: false })
            return
          }

          // Basic token validation - check if it looks like a JWT
          // This prevents unnecessary API calls with obviously invalid tokens
          const isValidTokenFormat = token.split('.').length === 3
          if (!isValidTokenFormat) {
            if (import.meta.env.DEV) {
              console.log('Invalid token format detected, clearing tokens')
            }
            localStorage.removeItem(config.auth.tokenKey)
            localStorage.removeItem(config.auth.refreshTokenKey)
            set({ isLoading: false })
            return
          }

          // Check if token is expired (basic check without verifying signature)
          try {
            const payload = JSON.parse(atob(token.split('.')[1]))
            const isExpired = payload.exp && payload.exp * 1000 < Date.now()

            if (isExpired) {
              if (import.meta.env.DEV) {
                console.log('Token expired, clearing tokens')
              }
              localStorage.removeItem(config.auth.tokenKey)
              localStorage.removeItem(config.auth.refreshTokenKey)
              set({ isLoading: false })
              return
            }
          } catch (e) {
            // If we can't parse the token payload, it's invalid
            if (import.meta.env.DEV) {
              console.log('Unable to parse token, clearing tokens')
            }
            localStorage.removeItem(config.auth.tokenKey)
            localStorage.removeItem(config.auth.refreshTokenKey)
            set({ isLoading: false })
            return
          }

          // Set tokens IMMEDIATELY and stop loading - this allows pages to render
          // The user fetch will happen in the background
          set({
            token,
            refreshToken,
            isLoading: false, // Allow UI to render immediately with token available
          })

          try {
            // Fetch user profile to restore session (in background)
            const { authService } = await import('@/services/authService')
            const user = await authService.getProfile()

            set({
              user,
              token,
              refreshToken,
              error: null,
            })
          } catch (error: any) {
            // More tolerant error handling - only clear tokens on actual auth errors
            if (import.meta.env.DEV) {
              console.log('Session restoration failed:', error)
            }

            // Only clear tokens if it's a 401 (Unauthorized) - not on network errors or 500s
            if (error?.status === 401) {
              if (import.meta.env.DEV) {
                console.log('Token invalid (401), clearing tokens')
              }
              localStorage.removeItem(config.auth.tokenKey)
              localStorage.removeItem(config.auth.refreshTokenKey)
              set({
                user: null,
                token: null,
                refreshToken: null,
                error: null,
              })
            } else {
              // For other errors (network, 500, etc.), keep tokens but log the error
              // The user might have a valid token but just experiencing network issues
              if (import.meta.env.DEV) {
                console.log('Network or server error, keeping tokens for retry')
              }
            }
          }
        } finally {
          isInitializing = false
        }
      },

      // Deprecated actions - kept for backward compatibility
      // TODO: Remove these in a future version after all components are migrated
      // Use React Query hooks instead: useLogin, useRegister, useRefreshToken
      login: async (email: string, password: string) => {
        console.warn('[WARNING] useAuthStore.login is deprecated. Use useLogin hook instead.')
        
        // Import dynamically to avoid circular dependencies
        const { authService } = await import('@/services/authService')
        
        set({ isLoading: true, error: null })

        try {
          const response = await authService.login({ email, password })

          set({
            user: response.user,
            token: response.access_token,
            refreshToken: response.refresh_token,
            isLoading: false,
            error: null,
          })

          // Store tokens in localStorage
          localStorage.setItem(config.auth.tokenKey, response.access_token)
          localStorage.setItem(config.auth.refreshTokenKey, response.refresh_token)

        } catch (error: unknown) {
          const errorMessage = error instanceof Error ? error.message : 'Error al iniciar sesión'
          set({
            isLoading: false,
            error: errorMessage,
          })
          throw error
        }
      },

      register: async (email: string, password: string, name: string) => {
        console.warn('[WARNING] useAuthStore.register is deprecated. Use useRegister hook instead.')
        
        // Import dynamically to avoid circular dependencies
        const { authService } = await import('@/services/authService')
        
        set({ isLoading: true, error: null })

        try {
          const response = await authService.register({ email, password, display_name: name })

          set({
            user: response.user,
            token: response.access_token,
            refreshToken: response.refresh_token,
            isLoading: false,
            error: null,
          })

          // Store tokens in localStorage
          localStorage.setItem(config.auth.tokenKey, response.access_token)
          localStorage.setItem(config.auth.refreshTokenKey, response.refresh_token)

        } catch (error: unknown) {
          const errorMessage = error instanceof Error ? error.message : 'Error al registrarse'
          set({
            isLoading: false,
            error: errorMessage,
          })
          throw error
        }
      },

      refreshTokenAction: async () => {
        console.warn('[WARNING] useAuthStore.refreshTokenAction is deprecated. Use useRefreshToken hook instead.')
        
        const { refreshToken: currentRefreshToken } = get()

        if (!currentRefreshToken) {
          throw new Error('No refresh token available')
        }

        try {
          // Import dynamically to avoid circular dependencies
          const { authService } = await import('@/services/authService')
          const response = await authService.refreshToken(currentRefreshToken)

          set({
            token: response.access_token,
            refreshToken: response.refresh_token,
          })

          // Update tokens in localStorage
          localStorage.setItem(config.auth.tokenKey, response.access_token)
          localStorage.setItem(config.auth.refreshTokenKey, response.refresh_token)

        } catch (error) {
          // If refresh fails, logout user
          get().logout()
          throw error
        }
      },
    }))

// Computed values (getters)
export const useIsAuthenticated = () => useAuthStore(state => !!state.token && !!state.user)
export const useCurrentUser = () => useAuthStore(state => state.user)
export const useAuthToken = () => useAuthStore(state => state.token)
export const useAuthError = () => useAuthStore(state => state.error)
export const useAuthLoading = () => useAuthStore(state => state.isLoading)