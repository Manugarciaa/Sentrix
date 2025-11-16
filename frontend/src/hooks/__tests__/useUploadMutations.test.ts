import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { 
  useUploadAnalysis, 
  useBatchUploadAnalyses, 
  useUploadCancellation,
  useUploadQueue 
} from '../useUploadMutations'
import { analysisService } from '@/services/analysisService'
import { mockAnalysis, mockDetection } from '@/test/utils'

// Mock the analysis service
vi.mock('@/services/analysisService')
const mockAnalysisService = vi.mocked(analysisService)

// Mock sonner toast
vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

// Mock XMLHttpRequest for upload progress tracking
const mockXHR = {
  open: vi.fn(),
  send: vi.fn(),
  setRequestHeader: vi.fn(),
  addEventListener: vi.fn(),
  upload: {
    addEventListener: vi.fn(),
  },
  status: 200,
  responseText: '',
  timeout: 0,
}

global.XMLHttpRequest = vi.fn(() => mockXHR) as any

// Mock environment variables
vi.mock('import.meta', () => ({
  env: {
    VITE_API_BASE_URL: 'http://localhost:8000',
  },
}))

// Mock localStorage
const mockLocalStorage = {
  getItem: vi.fn(() => 'mock-token'),
  setItem: vi.fn(),
  removeItem: vi.fn(),
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
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

// Mock file for testing
const createMockFile = (name: string = 'test.jpg', size: number = 1024) => {
  const file = new File(['test content'], name, { type: 'image/jpeg' })
  Object.defineProperty(file, 'size', { value: size })
  return file
}

describe('useUploadAnalysis', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = createTestQueryClient()
    vi.clearAllMocks()
    
    // Reset XMLHttpRequest mock
    mockXHR.status = 200
    mockXHR.responseText = JSON.stringify({
      id: 1,
      message: 'Analysis completed',
      analysis: mockAnalysis,
      detections: [mockDetection],
    })
  })

  afterEach(() => {
    queryClient.clear()
  })

  it('should upload analysis successfully', async () => {
    const { result } = renderHook(() => useUploadAnalysis(), {
      wrapper: createWrapper(queryClient),
    })

    const file = createMockFile()
    const uploadData = {
      file,
      confidence_threshold: 0.7,
      include_gps: true,
      latitude: -34.6037,
      longitude: -58.3816,
    }

    act(() => {
      result.current.mutate(uploadData)
    })

    expect(result.current.isPending).toBe(true)

    // Simulate successful upload
    const loadHandler = mockXHR.addEventListener.mock.calls.find(
      call => call[0] === 'load'
    )?.[1]
    
    if (loadHandler) {
      loadHandler()
    }

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(mockXHR.open).toHaveBeenCalledWith('POST', 'http://localhost:8000/api/v1/analyses')
    expect(mockXHR.setRequestHeader).toHaveBeenCalledWith('Authorization', 'Bearer mock-token')
    expect(mockXHR.send).toHaveBeenCalled()
  })

  it('should track upload progress', async () => {
    const onProgress = vi.fn()
    
    const { result } = renderHook(() => useUploadAnalysis(), {
      wrapper: createWrapper(queryClient),
    })

    const file = createMockFile()
    const uploadData = {
      file,
      onProgress,
    }

    act(() => {
      result.current.mutate(uploadData)
    })

    // Simulate progress events
    const progressHandler = mockXHR.upload.addEventListener.mock.calls.find(
      call => call[0] === 'progress'
    )?.[1]

    if (progressHandler) {
      progressHandler({
        lengthComputable: true,
        loaded: 512,
        total: 1024,
      })
    }

    expect(onProgress).toHaveBeenCalledWith(50)
  })

  it('should handle upload errors', async () => {
    const { result } = renderHook(() => useUploadAnalysis(), {
      wrapper: createWrapper(queryClient),
    })

    const file = createMockFile()

    act(() => {
      result.current.mutate({ file })
    })

    // Simulate error
    const errorHandler = mockXHR.addEventListener.mock.calls.find(
      call => call[0] === 'error'
    )?.[1]

    if (errorHandler) {
      errorHandler()
    }

    await waitFor(() => {
      expect(result.current.isError).toBe(true)
    })

    expect(result.current.error).toEqual(new Error('Network error occurred'))
  })

  it('should handle timeout errors', async () => {
    const { result } = renderHook(() => useUploadAnalysis(), {
      wrapper: createWrapper(queryClient),
    })

    const file = createMockFile()

    act(() => {
      result.current.mutate({ file })
    })

    // Simulate timeout
    const timeoutHandler = mockXHR.addEventListener.mock.calls.find(
      call => call[0] === 'timeout'
    )?.[1]

    if (timeoutHandler) {
      timeoutHandler()
    }

    await waitFor(() => {
      expect(result.current.isError).toBe(true)
    })

    expect(result.current.error).toEqual(new Error('Upload timeout'))
  })

  it('should handle server errors with status codes', async () => {
    mockXHR.status = 400
    mockXHR.responseText = JSON.stringify({
      message: 'Invalid file format',
    })

    const { result } = renderHook(() => useUploadAnalysis(), {
      wrapper: createWrapper(queryClient),
    })

    const file = createMockFile()

    act(() => {
      result.current.mutate({ file })
    })

    // Simulate load event with error status
    const loadHandler = mockXHR.addEventListener.mock.calls.find(
      call => call[0] === 'load'
    )?.[1]

    if (loadHandler) {
      loadHandler()
    }

    await waitFor(() => {
      expect(result.current.isError).toBe(true)
    })

    expect(result.current.error).toEqual(new Error('Invalid file format'))
  })

  it('should invalidate queries on successful upload', async () => {
    const invalidateQueriesSpy = vi.spyOn(queryClient, 'invalidateQueries')

    const { result } = renderHook(() => useUploadAnalysis(), {
      wrapper: createWrapper(queryClient),
    })

    const file = createMockFile()

    act(() => {
      result.current.mutate({ file })
    })

    // Simulate successful upload
    const loadHandler = mockXHR.addEventListener.mock.calls.find(
      call => call[0] === 'load'
    )?.[1]

    if (loadHandler) {
      loadHandler()
    }

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(invalidateQueriesSpy).toHaveBeenCalledWith({ 
      queryKey: ['analyses', 'list'] 
    })
    expect(invalidateQueriesSpy).toHaveBeenCalledWith({ 
      queryKey: ['reports', 'dashboard'] 
    })
  })
})

describe('useBatchUploadAnalyses', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = createTestQueryClient()
    vi.clearAllMocks()
    
    mockXHR.status = 200
    mockXHR.responseText = JSON.stringify({
      id: 1,
      message: 'Analysis completed',
      analysis: mockAnalysis,
      detections: [mockDetection],
    })
  })

  afterEach(() => {
    queryClient.clear()
  })

  it('should upload multiple files sequentially', async () => {
    const onProgress = vi.fn()
    const onItemProgress = vi.fn()

    const { result } = renderHook(() => useBatchUploadAnalyses(), {
      wrapper: createWrapper(queryClient),
    })

    const files = [
      createMockFile('test1.jpg'),
      createMockFile('test2.jpg'),
      createMockFile('test3.jpg'),
    ]

    const batchData = {
      files,
      options: { confidence_threshold: 0.7 },
      onProgress,
      onItemProgress,
    }

    act(() => {
      result.current.mutate(batchData)
    })

    expect(result.current.isPending).toBe(true)

    // Simulate successful uploads for all files
    for (let i = 0; i < files.length; i++) {
      const loadHandler = mockXHR.addEventListener.mock.calls.find(
        call => call[0] === 'load'
      )?.[1]

      if (loadHandler) {
        loadHandler()
      }
    }

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(onProgress).toHaveBeenCalled()
    expect(onItemProgress).toHaveBeenCalled()
    expect(mockXHR.send).toHaveBeenCalledTimes(3)
  })

  it('should handle partial failures in batch upload', async () => {
    const onProgress = vi.fn()

    const { result } = renderHook(() => useBatchUploadAnalyses(), {
      wrapper: createWrapper(queryClient),
    })

    const files = [
      createMockFile('test1.jpg'),
      createMockFile('test2.jpg'),
    ]

    act(() => {
      result.current.mutate({
        files,
        onProgress,
      })
    })

    // First file succeeds
    mockXHR.status = 200
    const loadHandler1 = mockXHR.addEventListener.mock.calls.find(
      call => call[0] === 'load'
    )?.[1]
    if (loadHandler1) loadHandler1()

    // Second file fails
    mockXHR.status = 500
    mockXHR.responseText = JSON.stringify({ message: 'Server error' })
    const loadHandler2 = mockXHR.addEventListener.mock.calls.find(
      call => call[0] === 'load'
    )?.[1]
    if (loadHandler2) loadHandler2()

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    const batchResult = result.current.data
    expect(batchResult?.successful).toBe(1)
    expect(batchResult?.failed).toBe(1)
    expect(batchResult?.errors).toContain('test2.jpg: Server error')
  })

  it('should track overall batch progress', async () => {
    const onProgress = vi.fn()

    const { result } = renderHook(() => useBatchUploadAnalyses(), {
      wrapper: createWrapper(queryClient),
    })

    const files = [createMockFile('test1.jpg'), createMockFile('test2.jpg')]

    act(() => {
      result.current.mutate({
        files,
        onProgress,
      })
    })

    // Complete first file
    const loadHandler = mockXHR.addEventListener.mock.calls.find(
      call => call[0] === 'load'
    )?.[1]
    if (loadHandler) loadHandler()

    // Check progress after first file
    expect(onProgress).toHaveBeenCalledWith(
      expect.objectContaining({
        totalFiles: 2,
        completedFiles: 1,
        overallProgress: 50,
      })
    )
  })
})

describe('useUploadCancellation', () => {
  it('should create cancellable upload', () => {
    const { result } = renderHook(() => useUploadCancellation())

    const uploadId = 'test-upload-1'
    const controller = result.current.createCancellableUpload(uploadId)

    expect(controller).toBeInstanceOf(AbortController)
    expect(controller.signal.aborted).toBe(false)
  })

  it('should cancel specific upload', () => {
    const { result } = renderHook(() => useUploadCancellation())

    const uploadId = 'test-upload-1'
    const controller = result.current.createCancellableUpload(uploadId)

    result.current.cancelUpload(uploadId)

    expect(controller.signal.aborted).toBe(true)
  })

  it('should cancel all uploads', () => {
    const { result } = renderHook(() => useUploadCancellation())

    const controller1 = result.current.createCancellableUpload('upload-1')
    const controller2 = result.current.createCancellableUpload('upload-2')

    result.current.cancelAllUploads()

    expect(controller1.signal.aborted).toBe(true)
    expect(controller2.signal.aborted).toBe(true)
  })
})

describe('useUploadQueue', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = createTestQueryClient()
    vi.clearAllMocks()
  })

  afterEach(() => {
    queryClient.clear()
  })

  it('should retry failed upload', async () => {
    mockAnalysisService.uploadAnalysis.mockResolvedValue({
      id: 1,
      message: 'Analysis completed',
      analysis: mockAnalysis,
      detections: [mockDetection],
    })

    const { result } = renderHook(() => useUploadQueue(), {
      wrapper: createWrapper(queryClient),
    })

    const file = createMockFile()
    const retryData = {
      file,
      options: { confidence_threshold: 0.8 },
    }

    act(() => {
      result.current.retryFailedUpload.mutate(retryData)
    })

    await waitFor(() => {
      expect(result.current.retryFailedUpload.isSuccess).toBe(true)
    })

    expect(mockAnalysisService.uploadAnalysis).toHaveBeenCalledWith({
      file,
      confidence_threshold: 0.8,
    })
  })

  it('should handle retry failures', async () => {
    const retryError = new Error('Retry failed')
    mockAnalysisService.uploadAnalysis.mockRejectedValue(retryError)

    const { result } = renderHook(() => useUploadQueue(), {
      wrapper: createWrapper(queryClient),
    })

    const file = createMockFile()

    act(() => {
      result.current.retryFailedUpload.mutate({ file })
    })

    await waitFor(() => {
      expect(result.current.retryFailedUpload.isError).toBe(true)
    })

    expect(result.current.retryFailedUpload.error).toEqual(retryError)
  })
})