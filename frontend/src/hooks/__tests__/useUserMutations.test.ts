import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { 
  useCreateUser, 
  useUpdateUser, 
  useDeleteUser, 
  useUpdateUserRole,
  useToggleUserStatus,
  useBulkUpdateUsers,
  useBulkDeleteUsers 
} from '../useUserMutations'
import { userService } from '@/services/userService'
import { useAppStore } from '@/store/app'
import { mockUser, mockAdminUser } from '@/test/utils'

// Mock the user service and app store
vi.mock('@/services/userService')
vi.mock('@/store/app')
vi.mock('@/hooks/useGlobalMutationDefaults', () => ({
  useAuthenticatedMutationDefaults: () => ({
    onError: vi.fn(),
    onSuccess: vi.fn(),
  }),
  createMutationOptions: vi.fn(),
}))

const mockUserService = vi.mocked(userService)
const mockUseAppStore = vi.mocked(useAppStore)

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

// Mock users list response
const mockUsersListResponse = {
  users: [mockUser, mockAdminUser],
  total: 2,
  page: 1,
  per_page: 10,
  total_pages: 1,
}

describe('useCreateUser', () => {
  let queryClient: QueryClient
  const mockAddNotification = vi.fn()

  beforeEach(() => {
    queryClient = createTestQueryClient()
    vi.clearAllMocks()

    // Set initial users list in cache
    queryClient.setQueryData(['users', 'list'], mockUsersListResponse)

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

  afterEach(() => {
    queryClient.clear()
  })

  it('should create user with optimistic updates', async () => {
    const newUser = {
      ...mockUser,
      id: '3',
      email: 'newuser@example.com',
      display_name: 'New User',
    }

    const createUserResponse = {
      user: newUser,
      message: 'User created successfully',
    }

    mockUserService.createUser.mockResolvedValue(createUserResponse)

    const { result } = renderHook(() => useCreateUser(), {
      wrapper: createWrapper(queryClient),
    })

    const createData = {
      email: 'newuser@example.com',
      password: 'password123',
      display_name: 'New User',
      role: 'USER' as const,
    }

    act(() => {
      result.current.mutate(createData)
    })

    // Should immediately add optimistic user to cache
    const cachedUsers = queryClient.getQueryData(['users', 'list']) as any
    exp