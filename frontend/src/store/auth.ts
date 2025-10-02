import { create } from 'zustand'
import type { User, AuthState } from '@/types'
import { config } from '@/lib/config'
import { authApi } from '@/api/auth'

interface AuthStore extends AuthState {
  // Actions
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name: string) => Promise<void>
  logout: () => void
  refreshTokenAction: () => Promise<void>
  updateUser: (userData: Partial<User>) => void
  initializeAuth: () => void
  clearError: () => void
}

export const useAuthStore = create<AuthStore>()((set, get) => ({
      // Initial state
      user: null,
      token: null,
      refreshToken: null,
      isLoading: false,
      error: null,

      // Actions
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null })

        try {
          const response = await authApi.login({ email, password })

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

        } catch (error: any) {
          set({
            isLoading: false,
            error: error.message || 'Error al iniciar sesión',
          })
          throw error
        }
      },

      register: async (email: string, password: string, name: string) => {
        set({ isLoading: true, error: null })

        try {
          const response = await authApi.register({ email, password, display_name: name })

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

        } catch (error: any) {
          set({
            isLoading: false,
            error: error.message || 'Error al registrarse',
          })
          throw error
        }
      },

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

        // Call logout API to invalidate token on server
        authApi.logout().catch(console.error)
      },

      refreshTokenAction: async () => {
        const { refreshToken: currentRefreshToken } = get()

        if (!currentRefreshToken) {
          throw new Error('No refresh token available')
        }

        try {
          const response = await authApi.refreshToken(currentRefreshToken)

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

      updateUser: (userData: Partial<User>) => {
        const { user } = get()
        if (user) {
          set({
            user: { ...user, ...userData }
          })
        }
      },

      initializeAuth: () => {
        const token = localStorage.getItem(config.auth.tokenKey)
        const refreshToken = localStorage.getItem(config.auth.refreshTokenKey)

        if (token && refreshToken) {
          set({
            token,
            refreshToken,
          })

          // Verify token and get user profile
          authApi.getProfile()
            .then(user => {
              set({ user, isLoading: false })
            })
            .catch(() => {
              // Token is invalid, clear it
              get().logout()
            })
        } else {
          set({ isLoading: false })
        }
      },

      clearError: () => {
        set({ error: null })
      },
    }))

// Computed values (getters)
export const useIsAuthenticated = () => useAuthStore(state => !!state.token && !!state.user)
export const useCurrentUser = () => useAuthStore(state => state.user)
export const useAuthToken = () => useAuthStore(state => state.token)
export const useAuthError = () => useAuthStore(state => state.error)
export const useAuthLoading = () => useAuthStore(state => state.isLoading)