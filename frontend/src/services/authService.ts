import { apiClient } from '@/api/client'
import { apiEndpoints } from '@/lib/config'
import type { User } from '@/types'

// Request/Response Types
export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  display_name?: string
}

export interface LoginResponse {
  user: User
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface RegisterResponse {
  user: User
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface RefreshTokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface ProfileUpdateData {
  display_name?: string
  full_name?: string
  organization?: string
}

export interface PasswordChangeData {
  current_password: string
  new_password: string
}

export interface ForgotPasswordData {
  email: string
}

export interface ResetPasswordData {
  token: string
  new_password: string
}

export interface VerifyEmailData {
  token: string
}

// Auth Service
export const authService = {
  // Authentication operations
  login: (credentials: LoginCredentials): Promise<LoginResponse> => {
    return apiClient.post(apiEndpoints.auth.login, credentials)
  },

  register: (data: RegisterData): Promise<RegisterResponse> => {
    return apiClient.post(apiEndpoints.auth.register, data)
  },

  logout: (): Promise<void> => {
    return apiClient.post(apiEndpoints.auth.logout)
  },

  refreshToken: (refreshToken: string): Promise<RefreshTokenResponse> => {
    return apiClient.post(apiEndpoints.auth.refresh, { refresh_token: refreshToken })
  },

  // Profile operations
  getProfile: (): Promise<User> => {
    return apiClient.get(apiEndpoints.auth.me)
  },

  updateProfile: (data: ProfileUpdateData): Promise<User> => {
    return apiClient.put(apiEndpoints.auth.me, data)
  },

  // Password operations
  changePassword: (data: PasswordChangeData): Promise<void> => {
    return apiClient.post('/api/v1/change-password', data)
  },

  forgotPassword: (data: ForgotPasswordData): Promise<void> => {
    return apiClient.post('/api/v1/forgot-password', data)
  },

  resetPassword: (data: ResetPasswordData): Promise<void> => {
    return apiClient.post('/api/v1/reset-password', data)
  },

  // Email verification
  verifyEmail: (data: VerifyEmailData): Promise<void> => {
    return apiClient.post('/api/v1/verify-email', data)
  },

  resendVerification: (email: string): Promise<void> => {
    return apiClient.post('/api/v1/resend-verification', { email })
  },
} as const