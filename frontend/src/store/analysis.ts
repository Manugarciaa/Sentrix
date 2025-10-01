import { create } from 'zustand'
import type { Analysis, AnalysisState, AnalysisFilters } from '@/types'

interface AnalysisStore extends AnalysisState {
  // Actions
  setAnalyses: (analyses: Analysis[]) => void
  addAnalysis: (analysis: Analysis) => void
  updateAnalysis: (id: string, updates: Partial<Analysis>) => void
  removeAnalysis: (id: string) => void
  setCurrentAnalysis: (analysis: Analysis | null) => void
  setFilters: (filters: Partial<AnalysisFilters>) => void
  clearFilters: () => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setPagination: (pagination: Partial<AnalysisState['pagination']>) => void
}

const initialFilters: AnalysisFilters = {
  risk_level: undefined,
  date_from: undefined,
  date_to: undefined,
  user_id: undefined,
  has_gps: undefined,
  validated_only: undefined,
}

export const useAnalysisStore = create<AnalysisStore>((set) => ({
  // Initial state
  analyses: [],
  currentAnalysis: null,
  filters: initialFilters,
  isLoading: false,
  error: null,
  pagination: {
    page: 1,
    total: 0,
    pages: 0,
  },

  // Actions
  setAnalyses: (analyses) => {
    set({ analyses, error: null })
  },

  addAnalysis: (analysis) => {
    set(state => ({
      analyses: [analysis, ...state.analyses],
      pagination: {
        ...state.pagination,
        total: state.pagination.total + 1,
      }
    }))
  },

  updateAnalysis: (id, updates) => {
    set(state => ({
      analyses: state.analyses.map(analysis =>
        analysis.id === id ? { ...analysis, ...updates } : analysis
      ),
      currentAnalysis: state.currentAnalysis?.id === id
        ? { ...state.currentAnalysis, ...updates }
        : state.currentAnalysis,
    }))
  },

  removeAnalysis: (id) => {
    set(state => ({
      analyses: state.analyses.filter(analysis => analysis.id !== id),
      currentAnalysis: state.currentAnalysis?.id === id ? null : state.currentAnalysis,
      pagination: {
        ...state.pagination,
        total: Math.max(0, state.pagination.total - 1),
      }
    }))
  },

  setCurrentAnalysis: (analysis) => {
    set({ currentAnalysis: analysis })
  },

  setFilters: (newFilters) => {
    set(state => ({
      filters: { ...state.filters, ...newFilters },
      pagination: { ...state.pagination, page: 1 }, // Reset to first page when filters change
    }))
  },

  clearFilters: () => {
    set({
      filters: initialFilters,
      pagination: { page: 1, total: 0, pages: 0 },
    })
  },

  setLoading: (loading) => {
    set({ isLoading: loading })
  },

  setError: (error) => {
    set({ error, isLoading: false })
  },

  setPagination: (newPagination) => {
    set(state => ({
      pagination: { ...state.pagination, ...newPagination }
    }))
  },
}))

// Computed selectors
export const useAnalyses = () => useAnalysisStore(state => state.analyses)
export const useCurrentAnalysis = () => useAnalysisStore(state => state.currentAnalysis)
export const useAnalysisFilters = () => useAnalysisStore(state => state.filters)
export const useAnalysisLoading = () => useAnalysisStore(state => state.isLoading)
export const useAnalysisError = () => useAnalysisStore(state => state.error)
export const useAnalysisPagination = () => useAnalysisStore(state => state.pagination)

// Helper selectors
export const useFilteredAnalyses = () => {
  return useAnalysisStore(state => {
    const { analyses, filters } = state

    return analyses.filter(analysis => {
      if (filters.risk_level && analysis.risk_assessment?.level !== filters.risk_level) {
        return false
      }

      // User ID filtering removed as Analysis no longer has user_id
      // if (filters.user_id && analysis.user_id !== filters.user_id) {
      //   return false
      // }

      if (filters.has_gps !== undefined && analysis.location?.has_location !== filters.has_gps) {
        return false
      }

      if (filters.date_from) {
        const analysisDate = new Date(analysis.created_at)
        const fromDate = new Date(filters.date_from)
        if (analysisDate < fromDate) {
          return false
        }
      }

      if (filters.date_to) {
        const analysisDate = new Date(analysis.created_at)
        const toDate = new Date(filters.date_to)
        if (analysisDate > toDate) {
          return false
        }
      }

      return true
    })
  })
}

export const useAnalysisStats = () => {
  return useAnalysisStore(state => {
    const analyses = state.analyses

    const total = analyses.length
    const withGPS = analyses.filter(a => a.location?.has_location).length
    const riskDistribution = analyses.reduce((acc, analysis) => {
      const level = analysis.risk_assessment?.level || 'BAJO'
      acc[level] = (acc[level] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    const avgProcessingTime = analyses.length > 0
      ? analyses.reduce((sum, a) => sum + (a.processing_time_ms || 0), 0) / analyses.length
      : 0

    return {
      total,
      withGPS,
      riskDistribution,
      avgProcessingTime,
    }
  })
}