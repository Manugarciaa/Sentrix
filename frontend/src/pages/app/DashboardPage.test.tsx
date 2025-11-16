import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@/test/utils'
import DashboardPage from './DashboardPage'
import { mockStats } from '@/test/utils'

// Mock the config
vi.mock('@/lib/config', () => ({
  config: {
    api: {
      baseUrl: 'http://localhost:8000',
    },
  },
}))

// Mock the auth store
vi.mock('@/store/auth', () => ({
  useAuthStore: () => ({
    user: {
      id: '1',
      name: 'Test User',
      email: 'test@example.com',
      role: 'USER',
    },
  }),
}))

// Mock fetch
global.fetch = vi.fn()

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state initially', () => {
    ;(global.fetch as any).mockImplementation(() =>
      new Promise(() => {}) // Never resolves
    )

    render(<DashboardPage />)
    expect(screen.getByText(/cargando/i)).toBeInTheDocument()
  })

  it('renders dashboard content after loading', async () => {
    ;(global.fetch as any).mockImplementation((url: string) => {
      if (url.includes('/stats')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockStats),
        })
      }
      if (url.includes('/analyses/recent')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ analyses: [] }),
        })
      }
      if (url.includes('/detections/map')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ detections: [] }),
        })
      }
      return Promise.reject(new Error('Not found'))
    })

    render(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByText(/dashboard/i)).toBeInTheDocument()
    })

    // Check if stats are displayed
    await waitFor(() => {
      expect(screen.getByText('42')).toBeInTheDocument() // total_analyses
      expect(screen.getByText('156')).toBeInTheDocument() // total_detections
    })
  })

  it('displays welcome message with user name', async () => {
    ;(global.fetch as any).mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockStats),
      })
    )

    render(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByText(/test user/i)).toBeInTheDocument()
    })
  })

  it('handles API errors gracefully', async () => {
    ;(global.fetch as any).mockImplementation(() =>
      Promise.reject(new Error('API Error'))
    )

    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

    render(<DashboardPage />)

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalled()
    })

    consoleSpy.mockRestore()
  })
})
