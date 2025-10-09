import { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// Create a test query client
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

interface AllTheProvidersProps {
  children: React.ReactNode
}

const AllTheProviders = ({ children }: AllTheProvidersProps) => {
  const testQueryClient = createTestQueryClient()

  return (
    <QueryClientProvider client={testQueryClient}>
      <BrowserRouter>{children}</BrowserRouter>
    </QueryClientProvider>
  )
}

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options })

export * from '@testing-library/react'
export { customRender as render }

// Mock user data
export const mockUser = {
  id: '1',
  email: 'test@sentrix.com',
  name: 'Test User',
  role: 'USER' as const,
  is_active: true,
  created_at: '2024-01-01T00:00:00Z',
  last_login: '2024-01-15T10:00:00Z',
}

export const mockAdminUser = {
  ...mockUser,
  id: '2',
  email: 'admin@sentrix.com',
  name: 'Admin User',
  role: 'ADMIN' as const,
}

export const mockExpertUser = {
  ...mockUser,
  id: '3',
  email: 'expert@sentrix.com',
  name: 'Expert User',
  role: 'EXPERT' as const,
}

// Mock analysis data
export const mockAnalysis = {
  id: '1',
  image_url: 'https://example.com/image.jpg',
  created_at: '2024-01-15T10:00:00Z',
  detection_count: 5,
  confidence_threshold: 0.7,
  status: 'completed' as const,
  has_gps: true,
  location: {
    latitude: -34.6037,
    longitude: -58.3816,
    address: 'Buenos Aires, Argentina',
  },
}

// Mock detection data
export const mockDetection = {
  id: '1',
  analysis_id: '1',
  confidence: 0.85,
  area_pixels: 1200,
  polygon: [
    [100, 100],
    [200, 100],
    [200, 200],
    [100, 200],
  ] as [number, number][],
  risk_level: 'high' as const,
  validation_status: 'pending_validation' as const,
  created_at: '2024-01-15T10:00:00Z',
}

// Mock stats data
export const mockStats = {
  total_analyses: 42,
  total_detections: 156,
  validated_detections: 89,
  created_reports: 12,
  pending_validations: 23,
  high_risk_detections: 45,
}
