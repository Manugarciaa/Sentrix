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

export const useAuthStore = create<AuthStore>()((set, get) => ({
      // Initial state
      user: null,
      token: null,
      refreshToken: null,
      isLoading: false,
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

      initializeAuth: () => {
        const token = localStorage.getItem(config.auth.tokenKey)
        const refreshToken = localStorage.getItem(config.auth.refreshTokenKey)

        if (token && refreshToken) {
          set({
            token,
            refreshToken,
            isLoading: false, // React Query will handle loading states
          })
        } else {
          set({ isLoading: false })
        }
      },

      // Deprecated actions - kept for backward compatibility
      // TODO: Remove these in a future version after all components are migrated
      // Use React Query hooks instead: useLogin, useRegister, useRefreshToken
      login: async (email: string, password: string) => {
        console.warn('⚠️ useAuthStore.login is deprecated. Use useLogin hook instead.')
        
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
        console.warn('⚠️ useAuthStore.register is deprecated. Use useRegister hook instead.')
        
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
        console.warn('⚠️ useAuthStore.refreshTokenAction is deprecated. Use useRefreshToken hook instead.')
        
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