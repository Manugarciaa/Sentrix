import { api } from './client'
import { apiEndpoints } from '@/lib/config'
import type { User } from '@/types'

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  user: User
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface RegisterRequest {
  email: string
  password: string
  display_name?: string
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

export const authApi = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    return api.post(apiEndpoints.auth.login, credentials)
  },

  register: async (userData: RegisterRequest): Promise<RegisterResponse> => {
    return api.post(apiEndpoints.auth.register, userData)
  },

  logout: async (): Promise<void> => {
    return api.post(apiEndpoints.auth.logout)
  },

  refreshToken: async (refreshToken: string): Promise<RefreshTokenResponse> => {
    return api.post(apiEndpoints.auth.refresh, { refresh_token: refreshToken })
  },

  getProfile: async (): Promise<User> => {
    return api.get(apiEndpoints.auth.me)
  },

  updateProfile: async (userData: Partial<User>): Promise<User> => {
    return api.put(apiEndpoints.auth.me, userData)
  },

  changePassword: async (currentPassword: string, newPassword: string): Promise<void> => {
    return api.post(`/api/v1/auth/change-password`, {
      current_password: currentPassword,
      new_password: newPassword,
    })
  },

  forgotPassword: async (email: string): Promise<void> => {
    return api.post('/auth/forgot-password', { email })
  },

  resetPassword: async (token: string, newPassword: string): Promise<void> => {
    return api.post('/auth/reset-password', {
      token,
      new_password: newPassword,
    })
  },

  verifyEmail: async (token: string): Promise<void> => {
    return api.post('/auth/verify-email', { token })
  },

  resendVerification: async (email: string): Promise<void> => {
    return api.post('/auth/resend-verification', { email })
  },
}