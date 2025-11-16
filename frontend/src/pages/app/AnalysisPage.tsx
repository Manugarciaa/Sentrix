import React, { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Search as SearchIcon, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Pagination } from '@/components/ui/Pagination'
import { SkeletonAnalysisList } from '@/components/ui/custom-skeletons'
import { AnalysisCard } from '@/components/domain/AnalysisCard'
import { FilterBar } from '@/components/domain/FilterBar'
import { EmptyState } from '@/components/domain/EmptyState'
import UploadModal from '@/components/domain/UploadModal'
import { useAnalysisStore } from '@/store/analysis'
import { apiEndpoints } from '@/lib/config'
import { apiClient } from '@/api/client'
import type { Analysis, PaginatedResponse } from '@/types'
import { useDebounce } from '@/hooks/useDebounce'

const AnalysisPage: React.FC = () => {
  const navigate = useNavigate()
  const [showUploadModal, setShowUploadModal] = useState(false)
  // Check if we've loaded data before in this session
  const [isInitialLoad, setIsInitialLoad] = useState(() => {
    return !sessionStorage.getItem('analyses_loaded')
  })

  // Zustand store
  const {
    analyses,
    filters,
    pagination,
    isLoading,
    setAnalyses,
    setFilters,
    setPage,
    setPerPage,
    clearFilters,
    setLoading,
    setError,
  } = useAnalysisStore()

  // Debounce filters to avoid excessive API calls
  const debouncedFilters = useDebounce(filters, 500)

  // Fetch analyses from backend
  const fetchAnalyses = useCallback(async () => {
    try {
      setLoading(true)

      // Build query params (backend uses limit/offset, not page/per_page)
      const offset = (pagination.page - 1) * pagination.per_page
      const params = new URLSearchParams({
        limit: String(pagination.per_page),
        offset: String(offset),
      })

      if (debouncedFilters.risk_level) params.append('risk_level', debouncedFilters.risk_level)
      if (debouncedFilters.date_from) params.append('since', debouncedFilters.date_from) // Backend uses 'since'
      if (debouncedFilters.date_to) params.append('until', debouncedFilters.date_to) // Backend uses 'until'
      if (debouncedFilters.user_id) params.append('user_id', String(debouncedFilters.user_id))
      if (debouncedFilters.has_gps) params.append('has_gps', 'true')
      if (debouncedFilters.validated_only) params.append('validated_only', 'true')

      // Use apiClient which automatically includes auth token
      const data: PaginatedResponse<Analysis> = await apiClient.get(
        `${apiEndpoints.analyses.list}?${params.toString()}`
      )

      setAnalyses(data)
      setIsInitialLoad(false)
      // Mark that we've loaded data at least once
      sessionStorage.setItem('analyses_loaded', 'true')
    } catch (error) {
      console.error('Error fetching analyses:', error)
      setError('Error de conexión')
      setIsInitialLoad(false)
    }
  }, [pagination.page, pagination.per_page, debouncedFilters, setLoading, setAnalyses, setError])

  useEffect(() => {
    fetchAnalyses()
  }, [fetchAnalyses])

  const handleFilterChange = (newFilters: any) => {
    setFilters(newFilters)
  }

  const handleResetFilters = () => {
    clearFilters()
  }

  const handlePageChange = (page: number) => {
    setPage(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handlePageSizeChange = (size: number) => {
    setPerPage(size)
  }

  // Only show full skeleton on true initial load (not on filters/pagination)
  if (isInitialLoad && isLoading) {
    return <SkeletonAnalysisList />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold text-foreground">Análisis</h1>
          <p className="text-base text-muted-foreground mt-2">
            Visualiza y gestiona los análisis procesados ({pagination.total} total)
          </p>
        </div>
        <Button
          onClick={() => setShowUploadModal(true)}
          className="gap-2"
        >
          <Plus className="h-4 w-4" />
          Nuevo Análisis
        </Button>
      </div>

      {/* Filter Bar */}
      <FilterBar
        filters={filters}
        onFilterChange={handleFilterChange}
        onReset={handleResetFilters}
      />

      {/* Analysis Grid */}
      {!isInitialLoad && isLoading ? (
        // Mostrar skeleton cards durante filtrado/paginación
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-card border border-border rounded-lg overflow-hidden shadow-sm">
              <div className="flex gap-3 p-3">
                {/* Image Thumbnail Skeleton */}
                <div className="w-24 h-24 rounded-md flex-shrink-0 bg-muted animate-pulse" />

                {/* Content Skeleton */}
                <div className="flex-1 min-w-0 flex flex-col justify-between">
                  {/* Header */}
                  <div>
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <div className="h-4 w-24 bg-muted rounded animate-pulse" />
                      <div className="h-5 w-16 bg-muted rounded-full animate-pulse" />
                    </div>

                    {/* Metadata compacta */}
                    <div className="flex items-center gap-3 mb-1">
                      <div className="h-3 w-20 bg-muted rounded animate-pulse" />
                      <div className="h-3 w-8 bg-muted rounded animate-pulse" />
                    </div>

                    <div className="h-3 w-32 bg-muted rounded animate-pulse" />
                  </div>

                  {/* Footer */}
                  <div className="h-3 w-28 bg-muted rounded animate-pulse" />
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : analyses.length === 0 ? (
        <EmptyState
          icon={SearchIcon}
          title="No se encontraron análisis"
          description="No hay análisis que coincidan con los filtros seleccionados. Intenta ajustar los filtros o crea un nuevo análisis."
          action={
            <div className="flex gap-3">
              <Button onClick={handleResetFilters} variant="outline">
                Limpiar Filtros
              </Button>
              <Button
                onClick={() => setShowUploadModal(true)}
              >
                <Plus className="h-4 w-4 mr-2" />
                Crear Análisis
              </Button>
            </div>
          }
        />
      ) : (
        <>
          {/* Analysis Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {analyses.map((analysis) => (
              <AnalysisCard
                key={analysis.id}
                analysis={analysis}
              />
            ))}
          </div>

          {/* Pagination */}
          {pagination.pages > 1 && (
            <div className="flex justify-center pt-4">
              <Pagination
                currentPage={pagination.page}
                totalPages={pagination.pages}
                onPageChange={handlePageChange}
                pageSize={pagination.per_page}
                onPageSizeChange={handlePageSizeChange}
                showPageSize
              />
            </div>
          )}
        </>
      )}

      {/* Upload Modal */}
      <UploadModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        onSuccess={() => {
          // Reset filters and pagination to ensure new analysis is visible
          clearFilters()
          setPage(1)
          // fetchAnalyses will be called automatically due to useEffect dependency changes
        }}
      />
    </div>
  )
}

export default AnalysisPage
