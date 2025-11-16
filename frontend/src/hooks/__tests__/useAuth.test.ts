import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useAuth, useIsAuthenticated, useCurrentUser } from '../useAuth'
import { authService } from '@/services/authService'
import { useAuthStore } from '@/store/auth'
import { mockUser } from '@/test/utils'

// Mock the auth service
vi.mock('@/services/authService')
const mockAuthService = vi.mocked(authService)

// Mock the auth store
vi.mock('@/store/auth')
const mockUseAuthStore = vi.mocked(useAuthStore)

// Create test query client
const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  })

// Test wrapper component
const createWrapper = (queryClient: QueryClient) => {
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('useAuth', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = createTestQueryClient()
    vi.clearAllMocks()
    
    // Setup default auth store mock
    mockUseAuthStore.mockImplementation((selector: any) => {
      const mockState = {
        token: 'mock-token',
        user: mockUser,
        isLoading: false,
        error: null,
        setUser: vi.fn(),
        logout: vi.fn(),
      }
      return selector ? selector(mockState) : mockState
    })
  })

  afterEach(() => {
    queryClient.clear()
  })

  describe('successful authentication', () => {
    it('should fetch user profile when token is available', async () => {
      mockAuthService.getProfile.mockResolvedValue(mockUser)

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(queryClient),
      })

      expect(result.current.isLoading).toBe(true)
      expect(result.current.user).toBeUndefined()

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      expect(result.current.user).toEqual(mockUser)
      expect(result.current.isAuthenticated).toBe(true)
      expect(result.current.isError).toBe(false)
      expect(mockAuthService.getProfile).toHaveBeenCalledTimes(1)
    })

    it('should sync user data with auth store on success', async () => {
      const mockSetUser = vi.fn()
      mockUseAuthStore.mockImplementation((selector: any) => {
        const mockState = {
          token: 'mock-token',
          user: null,
          isLoading: false,
          error: null,
          setUser: mockSetUser,
          logout: vi.fn(),
        }
        return selector ? selector(mockState) : mockState
      })

      mockAuthService.getProfile.mockResolvedValue(mockUser)

      renderHook(() => useAuth(), {
        wrapper: createWrapper(queryClient),
      })

      await waitFor(() => {
        expect(mockSetUser).toHaveBeenCalledWith(mockUser)
      })
    })

    it('should not fetch profile when no token is available', () => {
      mockUseAuthStore.mockImplementation((selector: any) => {
        const mockState = {
          token: null,
          user: null,
          isLoading: false,
          error: null,
          setUser: vi.fn(),
          logout: vi.fn(),
        }
        return selector ? selector(mockState) : mockState
      })

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(queryClient),
      })

      expect(result.current.isLoading).toBe(false)
      expect(result.current.isAuthenticated).toBe(false)
      expect(mockAuthService.getProfile).not.toHaveBeenCalled()
    })
  })

  describe('error handling', () => {
    it('should handle 401 errors by logging out user', async () => {
      const mockLogout = vi.fn()
      mockUseAuthStore.mockImplementation((selector: any) => {
        const mockState = {
          token: 'mock-token',
          user: null,
          isLoading: false,
          error: null,
          setUser: vi.fn(),
          logout: mockLogout,
        }
        return selector ? selector(mockState) : mockState
      })

      const authError = new Error('Unauthorized')
      ;(authError as any).status = 401
      mockAuthService.getProfile.mockRejectedValue(authError)

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(queryClient),
      })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })

      expect(mockLogout).toHaveBeenCalled()
      expect(queryClient.getQueryCache().getAll()).toHaveLength(0) // Cache should be cleared
    })

    it('should not retry on 401 errors', async () => {
      const authError = new Error('Unauthorized')
      ;(authError as any).status = 401
      mockAuthService.getProfile.mockRejectedValue(authError)

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(queryClient),
      })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })

      expect(mockAuthService.getProfile).toHaveBeenCalledTimes(1) // No retries
    })

    it('should retry on network errors up to 2 times', async () => {
      const networkError = new Error('Network error')
      ;(networkError as any).status = 500
      mockAuthService.getProfile.mockRejectedValue(networkError)

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(queryClient),
      })

      await waitFor(() => {
        expect(result.current.isError).toBe(true)
      })

      expect(mockAuthService.getProfile).toHaveBeenCalledTimes(3) // Initial + 2 retries
    })
  })

  describe('cache management', () => {
    it('should provide invalidate function', async () => {
      mockAuthService.getProfile.mockResolvedValue(mockUser)

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(queryClient),
      })

      await waitFor(() => {
        expect(result.current.user).toEqual(mockUser)
      })

      // Clear the mock to test invalidation
      mockAuthService.getProfile.mockClear()
      mockAuthService.getProfile.mockResolvedValue({ ...mockUser, display_name: 'Updated Name' })

      act(() => {
        result.current.invalidate()
      })

      await waitFor(() => {
        expect(mockAuthService.getProfile).toHaveBeenCalledTimes(1)
      })
    })

    it('should provide reset function', async () => {
      mockAuthService.getProfile.mockResolvedValue(mockUser)

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(queryClient),
      })

      await waitFor(() => {
        expect(result.current.user).toEqual(mockUser)
      })

      act(() => {
        result.current.reset()
      })

      expect(result.current.user).toBeUndefined()
      expect(result.current.isLoading).toBe(true)
    })
  })

  describe('refetch functionality', () => {
    it('should allow manual refetch', async () => {
      mockAuthService.getProfile.mockResolvedValue(mockUser)

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(queryClient),
      })

      await waitFor(() => {
        expect(result.current.user).toEqual(mockUser)
      })

      // Clear mock and setup new response
      mockAuthService.getProfile.mockClear()
      const updatedUser = { ...mockUser, display_name: 'Updated Name' }
      mockAuthService.getProfile.mockResolvedValue(updatedUser)

      act(() => {
        result.current.refetch()
      })

      await waitFor(() => {
        expect(result.current.user).toEqual(updatedUser)
      })

      expect(mockAuthService.getProfile).toHaveBeenCalledTimes(1)
    })
  })
})

describe('useIsAuthenticated', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should return true when both token and user exist', () => {
    mockUseAuthStore.mockImplementation((selector: any) => {
      const mockState = {
        token: 'mock-token',
        user: mockUser,
      }
      return selector(mockState)
    })

    const { result } = renderHook(() => useIsAuthenticated())

    expect(result.current).toBe(true)
  })

  it('should return false when token is missing', () => {
    mockUseAuthStore.mockImplementation((selector: any) => {
      const mockState = {
        token: null,
        user: mockUser,
      }
      return selector(mockState)
    })

    const { result } = renderHook(() => useIsAuthenticated())

    expect(result.current).toBe(false)
  })

  it('should return false when user is missing', () => {
    mockUseAuthStore.mockImplementation((selector: any) => {
      const mockState = {
        token: 'mock-token',
        user: null,
      }
      return selector(mockState)
    })

    const { result } = renderHook(() => useIsAuthenticated())

    expect(result.current).toBe(false)
  })
})

describe('useCurrentUser', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should return current user from store', () => {
    mockUseAuthStore.mockImplementation((selector: any) => {
      const mockState = {
        user: mockUser,
      }
      return selector(mockState)
    })

    const { result } = renderHook(() => useCurrentUser())

    expect(result.current).toEqual(mockUser)
  })

  it('should return null when no user is logged in', () => {
    mockUseAuthStore.mockImplementation((selector: any) => {
      const mockState = {
        user: null,
      }
      return selector(mockState)
    })

    const { result } = renderHook(() => useCurrentUser())

    expect(result.current).toBeNull()
  })
})