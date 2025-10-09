import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Search as SearchIcon } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Pagination } from '@/components/ui/Pagination'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { AnalysisCard } from '@/components/domain/AnalysisCard'
import { FilterBar } from '@/components/domain/FilterBar'
import { EmptyState } from '@/components/domain/EmptyState'
import { useAnalysisStore } from '@/store/analysis'
import { config, apiEndpoints } from '@/lib/config'
import type { Analysis, PaginatedResponse } from '@/types'

const AnalysisPage: React.FC = () => {
  const navigate = useNavigate()

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

  // Fetch analyses from backend
  const fetchAnalyses = async () => {
    try {
      setLoading(true)

      // Build query params (backend uses limit/offset, not page/per_page)
      const offset = (pagination.page - 1) * pagination.per_page
      const params = new URLSearchParams({
        limit: String(pagination.per_page),
        offset: String(offset),
      })

      if (filters.risk_level) params.append('risk_level', filters.risk_level)
      if (filters.date_from) params.append('since', filters.date_from) // Backend uses 'since'
      if (filters.user_id) params.append('user_id', String(filters.user_id))
      if (filters.has_gps) params.append('has_gps', 'true')

      const response = await fetch(
        `${config.api.baseUrl}${apiEndpoints.analyses.list}?${params.toString()}`
      )

      if (response.ok) {
        const data: PaginatedResponse<Analysis> = await response.json()
        setAnalyses(data)
      } else {
        setError('Error al cargar los análisis')
      }
    } catch (error) {
      console.error('Error fetching analyses:', error)
      setError('Error de conexión')
    }
  }

  useEffect(() => {
    fetchAnalyses()
  }, [pagination.page, pagination.per_page, filters])

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

  if (isLoading && analyses.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-sm text-gray-600">Cargando análisis...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold text-gray-900">Análisis</h1>
          <p className="text-base text-gray-700 mt-2">
            Visualiza y gestiona los análisis procesados ({pagination.total} total)
          </p>
        </div>
        <Button
          onClick={() => navigate('/app/uploads')}
          className="gap-2 bg-gradient-to-r from-primary-600 to-cyan-600 hover:from-primary-700 hover:to-cyan-700"
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
      {analyses.length === 0 ? (
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
                onClick={() => navigate('/app/uploads')}
                className="bg-gradient-to-r from-primary-600 to-cyan-600"
              >
                <Plus className="h-4 w-4 mr-2" />
                Crear Análisis
              </Button>
            </div>
          }
        />
      ) : (
        <>
          {/* Loading Overlay */}
          {isLoading && (
            <div className="relative">
              <div className="absolute inset-0 bg-white/60 backdrop-blur-sm z-10 flex items-center justify-center rounded-xl">
                <LoadingSpinner size="lg" />
              </div>
            </div>
          )}

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
    </div>
  )
}

export default AnalysisPage
