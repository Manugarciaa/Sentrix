/**
 * Unit tests for auth service
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { authService } from './authService'
import { apiClient } from '@/api/client'

// Mock apiClient
vi.mock('@/api/client', () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn(),
    put: vi.fn()
  }
}))

describe('AuthService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('login', () => {
    it('should call login endpoint with correct credentials', async () => {
      const mockResponse = {
        access_token: 'mock-token',
        refresh_token: 'mock-refresh',
        token_type: 'bearer',
        user: {
          id: '123',
          email: 'test@example.com',
          role: 'USER'
        }
      }

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse)

      const result = await authService.login({
        email: 'test@example.com',
        password: 'password123'
      })

      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/v1/token',
        expect.any(FormData)
      )
      expect(result).toEqual(mockResponse)
    })

    it('should handle login error', async () => {
      vi.mocked(apiClient.post).mockRejectedValue(new Error('Invalid credentials'))

      await expect(
        authService.login({
          email: 'wrong@example.com',
          password: 'wrongpass'
        })
      ).rejects.toThrow('Invalid credentials')
    })
  })

  describe('register', () => {
    it('should call register endpoint with user data', async () => {
      const mockResponse = {
        id: '123',
        email: 'newuser@example.com',
        role: 'USER'
      }

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse)

      const result = await authService.register({
        email: 'newuser@example.com',
        password: 'password123',
        display_name: 'New User'
      })

      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/v1/register',
        expect.objectContaining({
          email: 'newuser@example.com',
          display_name: 'New User'
        })
      )
      expect(result).toEqual(mockResponse)
    })
  })

  describe('getCurrentUser', () => {
    it('should fetch current user profile', async () => {
      const mockUser = {
        id: '123',
        email: 'test@example.com',
        role: 'USER',
        display_name: 'Test User'
      }

      vi.mocked(apiClient.get).mockResolvedValue(mockUser)

      const result = await authService.getCurrentUser()

      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/me')
      expect(result).toEqual(mockUser)
    })
  })

  describe('refreshToken', () => {
    it('should refresh access token', async () => {
      const mockResponse = {
        access_token: 'new-token',
        refresh_token: 'new-refresh',
        token_type: 'bearer'
      }

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse)

      const result = await authService.refreshToken('old-refresh-token')

      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/v1/token/refresh',
        { refresh_token: 'old-refresh-token' }
      )
      expect(result).toEqual(mockResponse)
    })
  })

  describe('updateProfile', () => {
    it('should update user profile', async () => {
      const mockUpdatedUser = {
        id: '123',
        email: 'test@example.com',
        role: 'USER',
        display_name: 'Updated Name',
        organization: 'New Org'
      }

      vi.mocked(apiClient.put).mockResolvedValue(mockUpdatedUser)

      const result = await authService.updateProfile({
        display_name: 'Updated Name',
        organization: 'New Org'
      })

      expect(apiClient.put).toHaveBeenCalledWith(
        '/api/v1/me',
        expect.objectContaining({
          display_name: 'Updated Name',
          organization: 'New Org'
        })
      )
      expect(result).toEqual(mockUpdatedUser)
    })
  })
})
