import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { 
  useLogin, 
  useRegister, 
  useLogout, 
  useUpdateProfile, 
  useChangePassword,
  useRefreshToken 
} from '../useAuthMutations'
import { authService } from '@/services/authService'
import { useAuthStore } from '@/store/auth'
import { useAppStore } from '@/store/app'
import { mockUser } from '@/test/utils'

// Mock the services and stores
vi.mock('@/services/authService')
vi.mock('@/store/auth')
vi.mock('@/store/app')
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  }
})

const mockAuthService = vi.mocked(authService)
const mockUseAuthStore = vi.mocked(useAuthStore)
const mockUseAppStore = vi.mocked(useAppStore)

// Mock localStorage
const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
})

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
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{children}</BrowserRouter>
    </QueryClientProvider>
  )
}

describe('useLogin', () => {
  let queryClient: QueryClient
  const mockNavigate = vi.fn()
  const mockSetState = vi.fn()
  const mockClearError = vi.fn()
  const mockAddNotification = vi.fn()

  beforeEach(() => {
    queryClient = createTestQueryClient()
    vi.clearAllMocks()

    // Mock auth store
    mockUseAuthStore.mockImplementation((selector?: any) => {
      if (selector) {
        return selector({
          clearError: mockClearError,
          setState: mockSetState,
        })
      }
      return {
        clearError: mockClearError,
        setState: mockSetState,
      }
    })

    // Mock app store
    mockUseAppStore.mockImplementation((selector?: any) => {
      if (selector) {
        return selector({
          addNotification: mockAddNotification,
        })
      }
      return {
        addNotification: mockAddNotification,
      }
    })

    // Mock navigate
    vi.doMock('react-router-dom', () => ({
      useNavigate: () => mockNavigate,
    }))
  })

  afterEach(() => {
    queryClient.clear()
  })

  it('should login successfully and navigate to dashboard', async () => {
    const loginResponse = {
      user: mockUser,
      access_token: 'access-token',
      refresh_token: 'refresh-token',
      token_type: 'Bearer',
      expires_in: 3600,
    }

    mockAuthService.login.mockResolvedValue(loginResponse)

    const { result } = renderHook(() => useLogin(), {
      wrapper: createWrapper(queryClient),
    })

    const credentials = { email: 'test@example.com', password: 'password' }

    act(() => {
      result.current.mutate(credentials)
    })

    expect(result.current.isPending).toBe(true)
    expect(mockClearError).toHaveBeenCalled()

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(mockAuthService.login).toHaveBeenCalledWith(credentials)
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith('access_token', 'access-token')
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith('refresh_token', 'refresh-token')
    expect(mockAddNotification).toHaveBeenCalledWith({
      type: 'success',
      title: 'Bienvenido',
      message: `Hola ${mockUser.display_name || mockUser.email}`,
      duration: 3000,
    })
    expect(mockNavigate).toHaveBeenCalledWith('/app/dashboard')
  })

  it('should handle login errors', async () => {
    const loginError = new Error('Invalid credentials')
    mockAuthService.login.mockRejectedValue(loginError)

    const { result } = renderHook(() => useLogin(), {
      wrapper: createWrapper(queryClient),
    })

    act(() => {
      result.current.mutate({ email: 'test@example.com', password: 'wrong' })
    })

    await waitFor(() => {
      expect(result.current.isError).toBe(true)
    })

    expect(mockAddNotification).toHaveBeenCalledWith({
      type: 'error',
      title: 'Error de autenticación',
      message: 'Invalid credentials',
      duration: 5000,
    })
  })

  it('should set loading state during login', async () => {
    mockAuthService.login.mockImplementation(() => new Promise(() => {})) // Never resolves

    const { result } = renderHook(() => useLogin(), {
      wrapper: createWrapper(queryClient),
    })

    act(() => {
      result.current.mutate({ email: 'test@example.com', password: 'password' })
    })

    expect(mockSetState).toHaveBeenCalledWith({ isLoading: true })
  })
})

describe('useRegister', () => {
  let queryClient: QueryClient
  const mockNavigate = vi.fn()
  const mockSetState = vi.fn()
  const mockClearError = vi.fn()
  const mockAddNotification = vi.fn()

  beforeEach(() => {
    queryClient = createTestQueryClient()
    vi.clearAllMocks()

    mockUseAuthStore.mockImplementation((selector?: any) => {
      if (selector) {
        return selector({
          clearError: mockClearError,
          setState: mockSetState,
        })
      }
      return {
        clearError: mockClearError,
        setState: mockSetState,
      }
    })

    mockUseAppStore.mockImplementation((selector?: any) => {
      if (selector) {
        return selector({
          addNotification: mockAddNotification,
        })
      }
      return {
        addNotification: mockAddNotification,
      }
    })
  })

  it('should register successfully', async () => {
    const registerResponse = {
      user: mockUser,
      access_token: 'access-token',
      refresh_token: 'refresh-token',
      token_type: 'Bearer',
      expires_in: 3600,
    }

    mockAuthService.register.mockResolvedValue(registerResponse)

    const { result } = renderHook(() => useRegister(), {
      wrapper: createWrapper(queryClient),
    })

    const registerData = {
      email: 'test@example.com',
      password: 'password',
      display_name: 'Test User',
    }

    act(() => {
      result.current.mutate(registerData)
    })

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(mockAuthService.register).toHaveBeenCalledWith(registerData)
    expect(mockAddNotification).toHaveBeenCalledWith({
      type: 'success',
      title: 'Cuenta creada',
      message: `Bienvenido ${mockUser.display_name || mockUser.email}`,
      duration: 3000,
    })
  })

  it('should handle registration errors', async () => {
    const registerError = new Error('Email already exists')
    mockAuthService.register.mockRejectedValue(registerError)

    const { result } = renderHook(() => useRegister(), {
      wrapper: createWrapper(queryClient),
    })

    act(() => {
      result.current.mutate({
        email: 'existing@example.com',
        password: 'password',
      })
    })

    await waitFor(() => {
      expect(result.current.isError).toBe(true)
    })

    expect(mockAddNotification).toHaveBeenCalledWith({
      type: 'error',
      title: 'Error de registro',
      message: 'Email already exists',
      duration: 5000,
    })
  })
})

describe('useLogout', () => {
  let queryClient: QueryClient
  const mockNavigate = vi.fn()
  const mockLogout = vi.fn()
  const mockAddNotification = vi.fn()

  beforeEach(() => {
    queryClient = createTestQueryClient()
    vi.clearAllMocks()

    mockUseAuthStore.mockImplementation((selector?: any) => {
      if (selector) {
        return selector({
          logout: mockLogout,
        })
      }
      return {
        logout: mockLogout,
      }
    })

    mockUseAppStore.mockImplementation((selector?: any) => {
      if (selector) {
        return selector({
          addNotification: mockAddNotification,
        })
      }
      return {
        addNotification: mockAddNotification,
      }
    })
  })

  it('should logout successfully', async () => {
    mockAuthService.logout.mockResolvedValue()

    const { result } = renderHook(() => useLogout(), {
      wrapper: createWrapper(queryClient),
    })

    act(() => {
      result.current.mutate()
    })

    // Should immediately clear auth state
    expect(mockLogout).toHaveBeenCalled()
    expect(mockNavigate).toHaveBeenCalledWith('/auth/login')

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(mockAddNotification).toHaveBeenCalledWith({
      type: 'success',
      title: 'Sesión cerrada',
      message: 'Has cerrado sesión correctamente',
      duration: 3000,
    })
  })

  it('should handle logout API errors gracefully', async () => {
    const logoutError = new Error('Server error')
    mockAuthService.logout.mockRejectedValue(logoutError)

    const { result } = renderHook(() => useLogout(), {
      wrapper: createWrapper(queryClient),
    })

    act(() => {
      result.current.mutate()
    })

    // Should still clear local state even if API fails
    expect(mockLogout).toHaveBeenCalled()
    expect(mockNavigate).toHaveBeenCalledWith('/auth/login')

    await waitFor(() => {
      expect(result.current.isError).toBe(true)
    })

    expect(mockAddNotification).toHaveBeenCalledWith({
      type: 'warning',
      title: 'Sesión cerrada',
      message: 'Tu sesión ha sido cerrada localmente',
      duration: 3000,
    })
  })
})

describe('useUpdateProfile', () => {
  let queryClient: QueryClient
  const mockUpdateUser = vi.fn()
  const mockSetUser = vi.fn()
  const mockAddNotification = vi.fn()

  beforeEach(() => {
    queryClient = createTestQueryClient()
    vi.clearAllMocks()

    // Set initial user data in cache
    queryClient.setQueryData(['auth', 'profile', 'me'], mockUser)

    mockUseAuthStore.mockImplementation((selector?: any) => {
      if (selector) {
        return selector({
          updateUser: mockUpdateUser,
          setUser: mockSetUser,
        })
      }
      return {
        updateUser: mockUpdateUser,
        setUser: mockSetUser,
      }
    })

    mockUseAppStore.mockImplementation((selector?: any) => {
      if (selector) {
        return selector({
          addNotification: mockAddNotification,
        })
      }
      return {
        addNotification: mockAddNotification,
      }
    })
  })

  it('should update profile with optimistic updates', async () => {
    const updatedUser = { ...mockUser, display_name: 'Updated Name' }
    mockAuthService.updateProfile.mockResolvedValue(updatedUser)

    const { result } = renderHook(() => useUpdateProfile(), {
      wrapper: createWrapper(queryClient),
    })

    const updateData = { display_name: 'Updated Name' }

    act(() => {
      result.current.mutate(updateData)
    })

    // Should immediately update cache optimistically
    const cachedUser = queryClient.getQueryData(['auth', 'profile', 'me'])
    expect(cachedUser).toEqual(expect.objectContaining(updateData))

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(mockAuthService.updateProfile).toHaveBeenCalledWith(updateData)
    expect(mockSetUser).toHaveBeenCalledWith(updatedUser)
    expect(mockAddNotification).toHaveBeenCalledWith({
      type: 'success',
      title: 'Perfil actualizado',
      message: 'Tu perfil ha sido actualizado correctamente',
      duration: 3000,
    })
  })

  it('should rollback optimistic updates on error', async () => {
    const updateError = new Error('Update failed')
    mockAuthService.updateProfile.mockRejectedValue(updateError)

    const { result } = renderHook(() => useUpdateProfile(), {
      wrapper: createWrapper(queryClient),
    })

    const updateData = { display_name: 'Updated Name' }

    act(() => {
      result.current.mutate(updateData)
    })

    await waitFor(() => {
      expect(result.current.isError).toBe(true)
    })

    // Should rollback to original user data
    const cachedUser = queryClient.getQueryData(['auth', 'profile', 'me'])
    expect(cachedUser).toEqual(mockUser)

    expect(mockAddNotification).toHaveBeenCalledWith({
      type: 'error',
      title: 'Error al actualizar perfil',
      message: 'Update failed',
      duration: 5000,
    })
  })
})

describe('useChangePassword', () => {
  let queryClient: QueryClient
  const mockAddNotification = vi.fn()

  beforeEach(() => {
    queryClient = createTestQueryClient()
    vi.clearAllMocks()

    mockUseAppStore.mockImplementation((selector?: any) => {
      if (selector) {
        return selector({
          addNotification: mockAddNotification,
        })
      }
      return {
        addNotification: mockAddNotification,
      }
    })
  })

  it('should change password successfully', async () => {
    mockAuthService.changePassword.mockResolvedValue()

    const { result } = renderHook(() => useChangePassword(), {
      wrapper: createWrapper(queryClient),
    })

    const passwordData = {
      current_password: 'oldpassword',
      new_password: 'newpassword',
    }

    act(() => {
      result.current.mutate(passwordData)
    })

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(mockAuthService.changePassword).toHaveBeenCalledWith(passwordData)
    expect(mockAddNotification).toHaveBeenCalledWith({
      type: 'success',
      title: 'Contraseña actualizada',
      message: 'Tu contraseña ha sido cambiada correctamente',
      duration: 3000,
    })
  })

  it('should handle password change errors', async () => {
    const passwordError = new Error('Current password is incorrect')
    mockAuthService.changePassword.mockRejectedValue(passwordError)

    const { result } = renderHook(() => useChangePassword(), {
      wrapper: createWrapper(queryClient),
    })

    act(() => {
      result.current.mutate({
        current_password: 'wrong',
        new_password: 'newpassword',
      })
    })

    await waitFor(() => {
      expect(result.current.isError).toBe(true)
    })

    expect(mockAddNotification).toHaveBeenCalledWith({
      type: 'error',
      title: 'Error al cambiar contraseña',
      message: 'Current password is incorrect',
      duration: 5000,
    })
  })
})

describe('useRefreshToken', () => {
  let queryClient: QueryClient
  const mockSetState = vi.fn()
  const mockLogout = vi.fn()
  const mockAddNotification = vi.fn()

  beforeEach(() => {
    queryClient = createTestQueryClient()
    vi.clearAllMocks()

    mockUseAuthStore.mockImplementation((selector?: any) => {
      if (selector) {
        return selector({
          setState: mockSetState,
          logout: mockLogout,
        })
      }
      return {
        setState: mockSetState,
        logout: mockLogout,
      }
    })

    mockUseAppStore.mockImplementation((selector?: any) => {
      if (selector) {
        return selector({
          addNotification: mockAddNotification,
        })
      }
      return {
        addNotification: mockAddNotification,
      }
    })

    // Mock window.location.href
    delete (window as any).location
    window.location = { href: '' } as any
  })

  it('should refresh token successfully', async () => {
    const refreshResponse = {
      access_token: 'new-access-token',
      refresh_token: 'new-refresh-token',
      token_type: 'Bearer',
      expires_in: 3600,
    }

    mockAuthService.refreshToken.mockResolvedValue(refreshResponse)

    const { result } = renderHook(() => useRefreshToken(), {
      wrapper: createWrapper(queryClient),
    })

    act(() => {
      result.current.mutate('old-refresh-token')
    })

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(mockAuthService.refreshToken).toHaveBeenCalledWith('old-refresh-token')
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith('access_token', 'new-access-token')
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith('refresh_token', 'new-refresh-token')
  })

  it('should logout user on refresh failure', async () => {
    const refreshError = new Error('Refresh token expired')
    mockAuthService.refreshToken.mockRejectedValue(refreshError)

    const { result } = renderHook(() => useRefreshToken(), {
      wrapper: createWrapper(queryClient),
    })

    act(() => {
      result.current.mutate('expired-refresh-token')
    })

    await waitFor(() => {
      expect(result.current.isError).toBe(true)
    })

    expect(mockLogout).toHaveBeenCalled()
    expect(mockAddNotification).toHaveBeenCalledWith({
      type: 'error',
      title: 'Sesión expirada',
      message: 'Tu sesión ha expirado. Por favor, inicia sesión nuevamente.',
      duration: 5000,
    })
    expect(window.location.href).toBe('/auth/login')
  })
})