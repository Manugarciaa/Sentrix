import { create } from 'zustand'
import type { Analysis, AnalysisFilters, PaginatedResponse } from '@/types'

interface AnalysisState {
  // Data
  analyses: Analysis[]
  currentAnalysis: Analysis | null
  filters: AnalysisFilters
  pagination: {
    page: number
    per_page: number
    total: number
    pages: number
  }

  // UI State
  isLoading: boolean
  isLoadingDetail: boolean
  error: string | null

  // Actions
  setAnalyses: (data: PaginatedResponse<Analysis>) => void
  setCurrentAnalysis: (analysis: Analysis | null) => void
  setFilters: (filters: Partial<AnalysisFilters>) => void
  setPage: (page: number) => void
  setPerPage: (perPage: number) => void
  clearFilters: () => void
  setLoading: (loading: boolean) => void
  setLoadingDetail: (loading: boolean) => void
  setError: (error: string | null) => void
  reset: () => void
}

const initialFilters: AnalysisFilters = {}

const initialPagination = {
  page: 1,
  per_page: 12,
  total: 0,
  pages: 0,
}

export const useAnalysisStore = create<AnalysisState>((set) => ({
  // Initial State
  analyses: [],
  currentAnalysis: null,
  filters: initialFilters,
  pagination: initialPagination,
  isLoading: false,
  isLoadingDetail: false,
  error: null,

  // Actions
  setAnalyses: (data) =>
    set({
      analyses: data.items,
      pagination: {
        page: data.page,
        per_page: data.per_page,
        total: data.total,
        pages: data.pages,
      },
      isLoading: false,
      error: null,
    }),

  setCurrentAnalysis: (analysis) =>
    set({
      currentAnalysis: analysis,
      isLoadingDetail: false,
      error: null,
    }),

  setFilters: (newFilters) =>
    set((state) => ({
      filters: { ...state.filters, ...newFilters },
      pagination: { ...state.pagination, page: 1 }, // Reset to page 1 when filters change
    })),

  setPage: (page) =>
    set((state) => ({
      pagination: { ...state.pagination, page },
    })),

  setPerPage: (per_page) =>
    set((state) => ({
      pagination: { ...state.pagination, per_page, page: 1 },
    })),

  clearFilters: () =>
    set({
      filters: initialFilters,
      pagination: initialPagination,
    }),

  setLoading: (isLoading) => set({ isLoading }),

  setLoadingDetail: (isLoadingDetail) => set({ isLoadingDetail }),

  setError: (error) =>
    set({
      error,
      isLoading: false,
      isLoadingDetail: false,
    }),

  reset: () =>
    set({
      analyses: [],
      currentAnalysis: null,
      filters: initialFilters,
      pagination: initialPagination,
      isLoading: false,
      isLoadingDetail: false,
      error: null,
    }),
}))
