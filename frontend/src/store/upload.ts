import { create } from 'zustand'
import type { Analysis, AnalysisResult } from '@/types'

export interface UploadOptions {
  confidence_threshold?: number
  include_gps?: boolean
  auto_recommendations?: boolean
}

export interface BatchItem {
  id: string
  file: File
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  result?: AnalysisResult
  error?: string
}

interface UploadState {
  // Single Upload State
  uploadProgress: number
  isUploading: boolean
  currentUpload: File | null
  uploadResult: AnalysisResult | null
  uploadError: string | null

  // Batch Upload State
  batchQueue: BatchItem[]
  isBatchProcessing: boolean
  batchProgress: {
    completed: number
    total: number
    failed: number
  }

  // Configuration
  config: UploadOptions

  // Single Upload Actions
  setCurrentUpload: (file: File | null) => void
  setUploadProgress: (progress: number) => void
  setUploading: (isUploading: boolean) => void
  setUploadResult: (result: AnalysisResult | null) => void
  setUploadError: (error: string | null) => void
  resetUpload: () => void

  // Batch Upload Actions
  addToBatch: (files: File[]) => void
  removeFromBatch: (id: string) => void
  updateBatchItem: (id: string, updates: Partial<BatchItem>) => void
  setBatchProcessing: (processing: boolean) => void
  resetBatch: () => void

  // Configuration Actions
  setConfig: (config: Partial<UploadOptions>) => void
  resetConfig: () => void
}

const defaultConfig: UploadOptions = {
  confidence_threshold: 0.7,
  include_gps: true,
  auto_recommendations: true,
}

export const useUploadStore = create<UploadState>((set, get) => ({
  // Initial Single Upload State
  uploadProgress: 0,
  isUploading: false,
  currentUpload: null,
  uploadResult: null,
  uploadError: null,

  // Initial Batch Upload State
  batchQueue: [],
  isBatchProcessing: false,
  batchProgress: {
    completed: 0,
    total: 0,
    failed: 0,
  },

  // Initial Configuration
  config: defaultConfig,

  // Single Upload Actions
  setCurrentUpload: (file) => set({ currentUpload: file }),

  setUploadProgress: (uploadProgress) => set({ uploadProgress }),

  setUploading: (isUploading) => set({ isUploading }),

  setUploadResult: (uploadResult) =>
    set({
      uploadResult,
      isUploading: false,
      uploadProgress: 100,
      uploadError: null,
    }),

  setUploadError: (uploadError) =>
    set({
      uploadError,
      isUploading: false,
      uploadProgress: 0,
    }),

  resetUpload: () =>
    set({
      uploadProgress: 0,
      isUploading: false,
      currentUpload: null,
      uploadResult: null,
      uploadError: null,
    }),

  // Batch Upload Actions
  addToBatch: (files) => {
    const newItems: BatchItem[] = files.map((file) => ({
      id: `${file.name}-${Date.now()}-${Math.random()}`,
      file,
      status: 'pending',
      progress: 0,
    }))

    set((state) => ({
      batchQueue: [...state.batchQueue, ...newItems],
      batchProgress: {
        ...state.batchProgress,
        total: state.batchProgress.total + newItems.length,
      },
    }))
  },

  removeFromBatch: (id) =>
    set((state) => {
      const item = state.batchQueue.find((i) => i.id === id)
      const newQueue = state.batchQueue.filter((i) => i.id !== id)

      return {
        batchQueue: newQueue,
        batchProgress: {
          ...state.batchProgress,
          total: state.batchProgress.total - 1,
          completed: item?.status === 'completed'
            ? state.batchProgress.completed - 1
            : state.batchProgress.completed,
          failed: item?.status === 'failed'
            ? state.batchProgress.failed - 1
            : state.batchProgress.failed,
        },
      }
    }),

  updateBatchItem: (id, updates) =>
    set((state) => {
      const itemIndex = state.batchQueue.findIndex((i) => i.id === id)
      if (itemIndex === -1) return state

      const oldItem = state.batchQueue[itemIndex]
      const newItem = { ...oldItem, ...updates }
      const newQueue = [...state.batchQueue]
      newQueue[itemIndex] = newItem

      // Update progress counters
      let completedDelta = 0
      let failedDelta = 0

      if (oldItem.status !== 'completed' && newItem.status === 'completed') {
        completedDelta = 1
      }
      if (oldItem.status !== 'failed' && newItem.status === 'failed') {
        failedDelta = 1
      }

      return {
        batchQueue: newQueue,
        batchProgress: {
          ...state.batchProgress,
          completed: state.batchProgress.completed + completedDelta,
          failed: state.batchProgress.failed + failedDelta,
        },
      }
    }),

  setBatchProcessing: (isBatchProcessing) => set({ isBatchProcessing }),

  resetBatch: () =>
    set({
      batchQueue: [],
      isBatchProcessing: false,
      batchProgress: {
        completed: 0,
        total: 0,
        failed: 0,
      },
    }),

  // Configuration Actions
  setConfig: (newConfig) =>
    set((state) => ({
      config: { ...state.config, ...newConfig },
    })),

  resetConfig: () => set({ config: defaultConfig }),
}))
