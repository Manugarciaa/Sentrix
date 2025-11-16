/**
 * Unit tests for auth store
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { useAuthStore } from './auth'

describe('AuthStore', () => {
  beforeEach(() => {
    // Reset store before each test
    const store = useAuthStore.getState()
    store.logout()
  })

  it('should initialize with null user', () => {
    const store = useAuthStore.getState()
    expect(store.user).toBeNull()
    expect(store.token).toBeNull()
    expect(store.isAuthenticated).toBe(false)
  })

  it('should set user and token on login', () => {
    const store = useAuthStore.getState()
    const mockUser = {
      id: '123',
      email: 'test@example.com',
      role: 'USER' as const,
      is_active: true,
      name: 'Test User'
    }
    const mockToken = 'mock-jwt-token'
    const mockRefreshToken = 'mock-refresh-token'

    store.setUser(mockUser)
    store.setTokens(mockToken, mockRefreshToken)

    expect(store.user).toEqual(mockUser)
    expect(store.token).toBe(mockToken)
    expect(store.refreshToken).toBe(mockRefreshToken)
    expect(store.isAuthenticated).toBe(true)
  })

  it('should clear user and token on logout', () => {
    const store = useAuthStore.getState()

    // First login
    store.setUser({
      id: '123',
      email: 'test@example.com',
      role: 'USER',
      is_active: true,
      name: 'Test User'
    })
    store.setTokens('token', 'refresh')

    // Then logout
    store.logout()

    expect(store.user).toBeNull()
    expect(store.token).toBeNull()
    expect(store.refreshToken).toBeNull()
    expect(store.isAuthenticated).toBe(false)
  })

  it('should persist token to localStorage', () => {
    const store = useAuthStore.getState()
    const mockToken = 'test-token'

    store.setTokens(mockToken, 'refresh-token')

    // Check localStorage
    expect(localStorage.getItem('token')).toBe(mockToken)
  })

  it('should handle user update', () => {
    const store = useAuthStore.getState()

    // Initial user
    store.setUser({
      id: '123',
      email: 'test@example.com',
      role: 'USER',
      is_active: true,
      name: 'Test User'
    })

    // Update user
    const updatedUser = {
      id: '123',
      email: 'test@example.com',
      role: 'ADMIN' as const,
      is_active: true,
      name: 'Admin User',
      display_name: 'Administrator'
    }

    store.setUser(updatedUser)

    expect(store.user?.role).toBe('ADMIN')
    expect(store.user?.display_name).toBe('Administrator')
  })

  it('should check if user is admin', () => {
    const store = useAuthStore.getState()

    // Regular user
    store.setUser({
      id: '123',
      email: 'user@example.com',
      role: 'USER',
      is_active: true
    })
    expect(store.user?.role).toBe('USER')

    // Admin user
    store.setUser({
      id: '456',
      email: 'admin@example.com',
      role: 'ADMIN',
      is_active: true
    })
    expect(store.user?.role).toBe('ADMIN')
  })

  it('should check if user is expert', () => {
    const store = useAuthStore.getState()

    store.setUser({
      id: '789',
      email: 'expert@example.com',
      role: 'EXPERT',
      is_active: true
    })

    expect(store.user?.role).toBe('EXPERT')
  })
})
