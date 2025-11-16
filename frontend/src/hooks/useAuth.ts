import { useQuery, useQueryClient } from '@tanstack/react-query'
import { authService } from '@/services/authService'
import { authKeys } from '@/lib/queryKeys'
import { useAuthStore } from '@/store/auth'
import type { User } from '@/types'

/**
 * Hook for fetching and managing user profile data with React Query
 * 
 * Features:
 * - Automatic token-based authentication
 * - Proper error handling for 401 errors
 * - Integration with existing auth store
 * - Optimized caching and stale time
 */
export const useAuth = () => {
  const token = useAuthStore(state => state.token)
  const queryClient = useQueryClient()
  
  const {
    data: user,
    isLoading,
    isError,
    error,
    refetch,
    isRefetching,
  } = useQuery({
    queryKey: authKeys.me(),
    queryFn: authService.getProfile,
    enabled: !!token, // Only run query if we have a token
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
    retry: (failureCount, error: any) => {
      // Don't retry on auth errors
      if (error?.status === 401 || error?.status === 403) {
        return false
      }
      // Retry up to 2 times for other errors
      return failureCount < 2
    },
    refetchOnWindowFocus: false,
    refetchOnReconnect: true,
    onSuccess: (userData: User) => {
      // Sync with auth store when query succeeds
      useAuthStore.getState().setUser(userData)
    },
    onError: (error: any) => {
      // Handle auth errors by clearing tokens
      if (error?.status === 401) {
        useAuthStore.getState().logout()
        queryClient.clear() // Clear all cached data on logout
      }
    },
  })

  // Computed values
  const isAuthenticated = !!token && !!user
  const isInitialLoading = isLoading && !user

  return {
    // Data
    user,
    isAuthenticated,
    
    // Loading states
    isLoading: isInitialLoading,
    isRefetching,
    
    // Error states
    isError,
    error,
    
    // Actions
    refetch,
    
    // Utilities
    invalidate: () => queryClient.invalidateQueries({ queryKey: authKeys.me() }),
    reset: () => queryClient.resetQueries({ queryKey: authKeys.me() }),
  }
}

/**
 * Hook for getting user permissions (if needed in the future)
 */
export const useUserPermissions = (userId?: string) => {
  const { isAuthenticated } = useAuth()
  
  return useQuery({
    queryKey: authKeys.userPermissions(userId || 'current'),
    queryFn: () => {
      // This would be implemented when permission system is added
      throw new Error('Permissions endpoint not implemented yet')
    },
    enabled: isAuthenticated && !!userId,
    staleTime: 10 * 60 * 1000, // 10 minutes for permissions
  })
}

/**
 * Lightweight hook for just checking authentication status
 * Useful for components that only need to know if user is logged in
 */
export const useIsAuthenticated = () => {
  const token = useAuthStore(state => state.token)
  const user = useAuthStore(state => state.user)
  
  return !!token && !!user
}

/**
 * Hook for getting current user data from store (synchronous)
 * Useful when you need immediate access to user data without loading states
 */
export const useCurrentUser = () => {
  return useAuthStore(state => state.user)
}

/**
 * Hook for getting auth token from store (synchronous)
 */
export const useAuthToken = () => {
  return useAuthStore(state => state.token)
}

/**
 * Hook for getting auth loading state from store
 */
export const useAuthLoading = () => {
  return useAuthStore(state => state.isLoading)
}

/**
 * Hook for getting auth error from store
 */
export const useAuthError = () => {
  return useAuthStore(state => state.error)
}