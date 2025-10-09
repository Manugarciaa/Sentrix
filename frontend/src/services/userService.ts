import { apiClient } from '@/api/client'
import type { User, UserRole, PaginatedResponse } from '@/types'

// Request/Response Types
export interface UserFilters {
  role?: UserRole
  is_active?: boolean
  search?: string
  page?: number
  per_page?: number
}

export interface CreateUserData {
  email: string
  password: string
  display_name?: string
  full_name?: string
  organization?: string
  role: UserRole
  is_active?: boolean
}

export interface UpdateUserData {
  display_name?: string
  full_name?: string
  organization?: string
  role?: UserRole
  is_active?: boolean
}

export interface UserResponse {
  user: User
  message?: string
}

export interface UsersListResponse extends PaginatedResponse<User> {}

// User Service
export const userService = {
  // User CRUD operations
  getUsers: (filters?: UserFilters): Promise<UsersListResponse> => {
    const params: Record<string, string> = {}
    
    if (filters) {
      if (filters.role) params.role = filters.role
      if (filters.is_active !== undefined) params.is_active = filters.is_active.toString()
      if (filters.search) params.search = filters.search
      if (filters.page) params.page = filters.page.toString()
      if (filters.per_page) params.per_page = filters.per_page.toString()
    }

    return apiClient.get('/api/v1/users', params)
  },

  getUser: (id: string): Promise<User> => {
    return apiClient.get(`/api/v1/users/${id}`)
  },

  createUser: (data: CreateUserData): Promise<UserResponse> => {
    return apiClient.post('/api/v1/users', data)
  },

  updateUser: (id: string, data: UpdateUserData): Promise<UserResponse> => {
    return apiClient.put(`/api/v1/users/${id}`, data)
  },

  deleteUser: (id: string): Promise<void> => {
    return apiClient.delete(`/api/v1/users/${id}`)
  },

  // User status operations
  activateUser: (id: string): Promise<UserResponse> => {
    return apiClient.post(`/api/v1/users/${id}/activate`)
  },

  deactivateUser: (id: string): Promise<UserResponse> => {
    return apiClient.post(`/api/v1/users/${id}/deactivate`)
  },

  // Role management
  updateUserRole: (id: string, role: UserRole): Promise<UserResponse> => {
    return apiClient.put(`/api/v1/users/${id}/role`, { role })
  },

  // Password management (admin operations)
  resetUserPassword: (id: string, newPassword: string): Promise<void> => {
    return apiClient.post(`/api/v1/users/${id}/reset-password`, { 
      new_password: newPassword 
    })
  },

  // Bulk operations
  bulkUpdateUsers: (userIds: string[], data: Partial<UpdateUserData>): Promise<UserResponse[]> => {
    return apiClient.put('/api/v1/users/bulk', {
      user_ids: userIds,
      ...data
    })
  },

  bulkDeleteUsers: (userIds: string[]): Promise<void> => {
    return apiClient.delete('/api/v1/users/bulk', {
      user_ids: userIds
    })
  },

  // User statistics and analytics
  getUserStats: (): Promise<{
    total_users: number
    active_users: number
    users_by_role: Record<UserRole, number>
    recent_registrations: number
  }> => {
    return apiClient.get('/api/v1/users/stats')
  },

  // User activity
  getUserActivity: (id: string, filters?: {
    date_from?: string
    date_to?: string
    activity_type?: string
  }): Promise<any[]> => {
    const params: Record<string, string> = {}
    
    if (filters) {
      if (filters.date_from) params.date_from = filters.date_from
      if (filters.date_to) params.date_to = filters.date_to
      if (filters.activity_type) params.activity_type = filters.activity_type
    }

    return apiClient.get(`/api/v1/users/${id}/activity`, params)
  },
} as const