import React, { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge, getRiskLevelBadge } from '@/components/ui/Badge'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { analysesApi } from '@/api/analyses'
import {
  Search,
  Download,
  Eye,
  MapPin,
  Camera,
  Calendar,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock,
  RefreshCw
} from 'lucide-react'

type FilterOption = 'all' | 'high-risk' | 'with-gps' | 'recent'
type SortOption = 'newest' | 'oldest' | 'risk-desc' | 'risk-asc' | 'detections'

const AnalysisPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedFilter, setSelectedFilter] = useState<FilterOption>('all')
  const [sortBy, setSortBy] = useState<SortOption>('newest')
  const [selectedRisk] = useState<string>('')

  // Fetch analyses with real-time updates
  const {
    data: analysesData,
    isLoading,
    error,
    refetch
  } = useQuery({
    queryKey: ['analyses', selectedFilter, selectedRisk, sortBy],
    queryFn: async () => {
      switch (selectedFilter) {
        case 'high-risk':
          return analysesApi.getByRiskLevel('ALTO', 50)
        case 'with-gps':
          return analysesApi.getWithGPS(50)
        case 'recent':
          return analysesApi.getRecent(20)
        default:
          return analysesApi.list({
            limit: 50,
            risk_level: selectedRisk as any
          })
      }
    },
    refetchInterval: 15000, // Refresh every 15 seconds for real-time updates
  })

  // Filter and sort analyses
  const filteredAnalyses = useMemo(() => {
    if (!analysesData) return []

    const analyses = Array.isArray(analysesData) ? analysesData : analysesData.analyses || analysesData.items || []
    let filtered = analyses

    // Apply search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      filtered = filtered.filter((analysis: any) =>
        analysis.image_filename?.toLowerCase().includes(term) ||
        analysis.location?.coordinates?.includes(term) ||
        analysis.camera_info?.camera_make?.toLowerCase().includes(term)
      )
    }

    // Apply sorting
    return filtered.sort((a: any, b: any) => {
      switch (sortBy) {
        case 'newest':
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        case 'oldest':
          return new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        case 'risk-desc':
          const riskOrder: Record<string, number> = { 'ALTO': 4, 'MEDIO': 3, 'BAJO': 2, 'MINIMO': 1 }
          return (riskOrder[b.risk_assessment?.level] || 0) - (riskOrder[a.risk_assessment?.level] || 0)
        case 'risk-asc':
          const riskOrderAsc: Record<string, number> = { 'ALTO': 4, 'MEDIO': 3, 'BAJO': 2, 'MINIMO': 1 }
          return (riskOrderAsc[a.risk_assessment?.level] || 0) - (riskOrderAsc[b.risk_assessment?.level] || 0)
        case 'detections':
          return (b.risk_assessment?.total_detections || 0) - (a.risk_assessment?.total_detections || 0)
        default:
          return 0
      }
    })
  }, [analysesData, searchTerm, sortBy])

  // Statistics calculations
  const stats = useMemo(() => {
    if (!analysesData) return null

    const analyses = Array.isArray(analysesData) ? analysesData : analysesData.analyses || analysesData.items || []
    const totalAnalyses = analyses.length
    const highRiskCount = analyses.filter((a: any) => a.risk_assessment?.level === 'ALTO').length
    const withGpsCount = analyses.filter((a: any) => a.location?.has_location).length
    const totalDetections = analyses.reduce((sum: any, a: any) => sum + (a.risk_assessment?.total_detections || 0), 0)

    return {
      totalAnalyses,
      highRiskCount,
      withGpsCount,
      totalDetections,
      avgProcessingTime: analyses.reduce((sum: any, a: any) => sum + (a.processing_time_ms || 0), 0) / analyses.length
    }
  }, [analysesData])

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString('es-PE', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const formatProcessingTime = (ms: number) => {
    if (ms < 1000) return `${ms}ms`
    return `${(ms / 1000).toFixed(1)}s`
  }

  const getRiskIcon = (level: string) => {
    switch (level) {
      case 'ALTO':
        return <AlertTriangle className="h-4 w-4 text-red-500" />
      case 'MEDIO':
        return <TrendingUp className="h-4 w-4 text-yellow-500" />
      case 'BAJO':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestión de Análisis</h1>
          <p className="text-gray-600">
            Administración detallada de procesamiento de imágenes y detecciones
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button onClick={() => refetch()} variant="outline" className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4" />
            Actualizar
          </Button>
          <Button className="flex items-center gap-2">
            <Camera className="h-4 w-4" />
            Nuevo Análisis
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="h-8 w-8 flex items-center justify-center bg-blue-100 rounded-lg">
                    <Eye className="h-4 w-4 text-blue-600" />
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Total Análisis</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.totalAnalyses}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="h-8 w-8 flex items-center justify-center bg-red-100 rounded-lg">
                    <AlertTriangle className="h-4 w-4 text-red-600" />
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Alto Riesgo</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.highRiskCount}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="h-8 w-8 flex items-center justify-center bg-green-100 rounded-lg">
                    <MapPin className="h-4 w-4 text-green-600" />
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Con GPS</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.withGpsCount}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="h-8 w-8 flex items-center justify-center bg-purple-100 rounded-lg">
                    <TrendingUp className="h-4 w-4 text-purple-600" />
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Detecciones</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.totalDetections}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="h-8 w-8 flex items-center justify-center bg-yellow-100 rounded-lg">
                    <Clock className="h-4 w-4 text-yellow-600" />
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Tiempo Prom.</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatProcessingTime(stats.avgProcessingTime)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters and Search */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4 items-center">
            {/* Search */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar por nombre, ubicación o cámara..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Filter buttons */}
            <div className="flex gap-2">
              <Button
                variant={selectedFilter === 'all' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedFilter('all')}
              >
                Todos
              </Button>
              <Button
                variant={selectedFilter === 'recent' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedFilter('recent')}
              >
                Recientes
              </Button>
              <Button
                variant={selectedFilter === 'high-risk' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedFilter('high-risk')}
              >
                Alto Riesgo
              </Button>
              <Button
                variant={selectedFilter === 'with-gps' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedFilter('with-gps')}
              >
                Con GPS
              </Button>
            </div>

            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as SortOption)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="newest">Más recientes</option>
              <option value="oldest">Más antiguos</option>
              <option value="risk-desc">Mayor riesgo</option>
              <option value="risk-asc">Menor riesgo</option>
              <option value="detections">Más detecciones</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Resultados ({filteredAnalyses.length})</span>
            <Button variant="outline" size="sm" className="flex items-center gap-2">
              <Download className="h-4 w-4" />
              Exportar
            </Button>
          </CardTitle>
          <CardDescription>
            Actualización automática cada 15 segundos
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <LoadingSpinner size="lg" text="Cargando análisis..." />
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <p className="text-red-600">Error al cargar los análisis</p>
              <Button onClick={() => refetch()} className="mt-4">
                Reintentar
              </Button>
            </div>
          ) : filteredAnalyses.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500">No se encontraron análisis</p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredAnalyses.map((analysis: any) => (
                <div
                  key={analysis.id}
                  className={`border rounded-lg p-4 transition-colors cursor-pointer ${
                    analysis.status === 'failed' ? 'border-red-200 bg-red-50' :
                    analysis.status === 'processing' ? 'border-blue-200 bg-blue-50' :
                    analysis.status === 'pending' ? 'border-yellow-200 bg-yellow-50' :
                    'border-gray-200 hover:bg-gray-50'
                  }`}
                  onClick={() => window.open(`/app/analysis/${analysis.id}`, '_blank')}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      {analysis.status === 'processing' ? (
                        <Clock className="h-5 w-5 text-blue-500 animate-spin" />
                      ) : analysis.status === 'pending' ? (
                        <Clock className="h-5 w-5 text-yellow-500" />
                      ) : analysis.status === 'failed' ? (
                        <XCircle className="h-5 w-5 text-red-500" />
                      ) : (
                        getRiskIcon(analysis.risk_assessment?.level || 'BAJO')
                      )}
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-medium text-gray-900">
                            {analysis.image_filename}
                          </h3>
                          {analysis.status === 'processing' && analysis.processing_progress && (
                            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                              {analysis.processing_progress}%
                            </span>
                          )}
                          {analysis.processing_queue_position && (
                            <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                              Cola: #{analysis.processing_queue_position}
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-500 mt-1">
                          <span className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            {formatDate(analysis.created_at)}
                          </span>
                          {analysis.status === 'completed' && (
                            <>
                              <span>
                                {analysis.risk_assessment?.total_detections || 0} detecciones
                              </span>
                              <span>
                                {formatProcessingTime(analysis.processing_time_ms || 0)}
                              </span>
                            </>
                          )}
                          {analysis.status === 'failed' && (
                            <span className="text-red-600">
                              Error: {analysis.error_message}
                            </span>
                          )}
                          {analysis.location?.has_location && (
                            <span className="flex items-center gap-1 text-blue-600">
                              <MapPin className="h-3 w-3" />
                              GPS
                            </span>
                          )}
                          {analysis.camera_info && (
                            <span className="flex items-center gap-1 text-purple-600">
                              <Camera className="h-3 w-3" />
                              {analysis.camera_info.camera_make}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      {analysis.status === 'completed' && (
                        <Badge variant={getRiskLevelBadge(analysis.risk_assessment?.level || 'BAJO') as any}>
                          {analysis.risk_assessment?.level || 'BAJO'}
                        </Badge>
                      )}
                      {analysis.status === 'processing' && (
                        <Badge variant="outline" className="text-blue-600 border-blue-200">
                          Procesando
                        </Badge>
                      )}
                      {analysis.status === 'pending' && (
                        <Badge variant="outline" className="text-yellow-600 border-yellow-200">
                          En Cola
                        </Badge>
                      )}
                      {analysis.status === 'failed' && (
                        <Badge variant="outline" className="text-red-600 border-red-200">
                          Error
                        </Badge>
                      )}
                      <Eye className="h-4 w-4 text-gray-400" />
                    </div>
                  </div>

                  {/* Risk Assessment Details */}
                  {(analysis.risk_assessment?.total_detections || 0) > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-100">
                      <div className="flex items-center gap-6 text-sm">
                        {analysis.risk_assessment?.risk_score && (
                          <span className="text-gray-600">
                            Score: <span className="font-medium text-gray-900">
                              {analysis.risk_assessment.risk_score.toFixed(2)}
                            </span>
                          </span>
                        )}
                        {(analysis.risk_assessment?.high_risk_count || 0) > 0 && (
                          <span className="text-red-600">
                            {analysis.risk_assessment.high_risk_count} alto riesgo
                          </span>
                        )}
                        {(analysis.risk_assessment?.medium_risk_count || 0) > 0 && (
                          <span className="text-yellow-600">
                            {analysis.risk_assessment.medium_risk_count} medio riesgo
                          </span>
                        )}
                        <span className="text-gray-600">
                          Modelo: {analysis.model_used || 'N/A'}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default AnalysisPage