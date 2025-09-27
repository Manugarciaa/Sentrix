import React, { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import HeatMap from '@/components/map/HeatMap'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import {
  transformAnalysisToHeatData,
  filterByDateRange,
  filterByRiskLevel,
  getHeatDataStats,
  generateMockHeatData,
  type HeatMapData
} from '@/utils/mapDataTransform'
import { Calendar, Filter, MapPin, TrendingUp, AlertTriangle, BarChart3 } from 'lucide-react'

const MapPage: React.FC = () => {
  // Filters state
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // Last 30 days
    end: new Date()
  })
  const [selectedRiskLevels, setSelectedRiskLevels] = useState<('ALTO' | 'MEDIO' | 'BAJO')[]>([
    'ALTO', 'MEDIO', 'BAJO'
  ])

  // Fetch analyses data (for now using mock data)
  const { data: analyses, isLoading } = useQuery({
    queryKey: ['analyses-for-map'],
    queryFn: async () => {
      // For now, use mock data. In production, this would fetch from the real API
      const mockData = generateMockHeatData()
      return mockData
    },
    refetchInterval: 60000 // Refresh every minute
  })

  // Transform and filter data
  const heatData = useMemo(() => {
    if (!analyses) return []

    let filteredData = analyses as HeatMapData[]

    // Apply date filter
    if (dateRange.start && dateRange.end) {
      filteredData = filterByDateRange(filteredData, dateRange.start, dateRange.end)
    }

    // Apply risk level filter
    filteredData = filterByRiskLevel(filteredData, selectedRiskLevels)

    return filteredData
  }, [analyses, dateRange, selectedRiskLevels])

  // Calculate statistics
  const stats = useMemo(() => getHeatDataStats(heatData), [heatData])

  const handleRiskLevelToggle = (level: 'ALTO' | 'MEDIO' | 'BAJO') => {
    setSelectedRiskLevels(prev =>
      prev.includes(level)
        ? prev.filter(l => l !== level)
        : [...prev, level]
    )
  }

  const resetFilters = () => {
    setDateRange({
      start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
      end: new Date()
    })
    setSelectedRiskLevels(['ALTO', 'MEDIO', 'BAJO'])
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Cargando mapa..." />
      </div>
    )
  }

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Header */}

      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Quick Stats */}
            <div className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Resumen</h3>
              <div className="space-y-4">
                <div>
                  <div className="text-3xl font-bold text-primary-600">{stats.totalPoints}</div>
                  <div className="text-sm text-gray-600">Ubicaciones monitoreadas</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900">{stats.totalDetections}</div>
                  <div className="text-sm text-gray-600">Total detecciones</div>
                </div>
              </div>
            </div>

            {/* Risk Level Filter */}
            <div className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Filter className="h-5 w-5 mr-2" />
                Filtrar por Riesgo
              </h3>
              <div className="space-y-3">
                {[
                  { level: 'ALTO' as const, color: 'bg-red-500', label: 'Alto', count: stats.riskCounts.ALTO },
                  { level: 'MEDIO' as const, color: 'bg-yellow-500', label: 'Medio', count: stats.riskCounts.MEDIO },
                  { level: 'BAJO' as const, color: 'bg-green-500', label: 'Bajo', count: stats.riskCounts.BAJO }
                ].map(({ level, color, label, count }) => (
                  <label key={level} className="flex items-center justify-between cursor-pointer p-2 rounded-lg hover:bg-gray-50 transition-colors">
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        checked={selectedRiskLevels.includes(level)}
                        onChange={() => handleRiskLevelToggle(level)}
                        className="mr-3"
                      />
                      <div className={`w-4 h-4 rounded-full ${color} mr-3`}></div>
                      <span className="text-sm font-medium text-gray-700">{label} Riesgo</span>
                    </div>
                    <span className="text-sm font-semibold text-gray-900">{count}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Date Range Filter */}
            <div className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Calendar className="h-5 w-5 mr-2" />
                Período
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-700 block mb-2">Desde</label>
                  <input
                    type="date"
                    value={dateRange.start.toISOString().split('T')[0]}
                    onChange={(e) => setDateRange(prev => ({
                      ...prev,
                      start: new Date(e.target.value)
                    }))}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700 block mb-2">Hasta</label>
                  <input
                    type="date"
                    value={dateRange.end.toISOString().split('T')[0]}
                    onChange={(e) => setDateRange(prev => ({
                      ...prev,
                      end: new Date(e.target.value)
                    }))}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={resetFilters}
                  className="w-full"
                >
                  Resetear Filtros
                </Button>
              </div>
            </div>

            {/* Intensity Indicator */}
            <div className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Intensidad Promedio</h3>
              <div className="text-center">
                <div className="text-3xl font-bold text-primary-600 mb-2">
                  {(stats.avgIntensity * 100).toFixed(1)}%
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-green-500 via-yellow-500 to-red-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${stats.avgIntensity * 100}%` }}
                  ></div>
                </div>
                <div className="text-xs text-gray-600 mt-2">Nivel de riesgo en la zona</div>
              </div>
            </div>
          </div>

          {/* Map Area */}
          <div className="lg:col-span-4">
            <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
              <HeatMap
                data={heatData}
                center={[-26.8083, -65.2176]} // Tucumán, Argentina
                zoom={12}
                className="h-[700px] w-full"
              />
            </div>

            {/* Map Info */}
            <div className="mt-8 bg-white rounded-xl p-6 border border-gray-100 shadow-sm">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                    <AlertTriangle className="h-5 w-5 mr-2 text-primary-600" />
                    Cómo interpretar
                  </h4>
                  <ul className="text-sm text-gray-600 space-y-2">
                    <li className="flex items-start">
                      <div className="w-3 h-3 bg-red-500 rounded-full mr-3 mt-1.5 flex-shrink-0"></div>
                      Zonas rojas: Alta concentración de criaderos
                    </li>
                    <li className="flex items-start">
                      <div className="w-3 h-3 bg-yellow-500 rounded-full mr-3 mt-1.5 flex-shrink-0"></div>
                      Zonas amarillas: Riesgo moderado
                    </li>
                    <li className="flex items-start">
                      <div className="w-3 h-3 bg-green-500 rounded-full mr-3 mt-1.5 flex-shrink-0"></div>
                      Zonas verdes: Bajo riesgo
                    </li>
                  </ul>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                    <TrendingUp className="h-5 w-5 mr-2 text-primary-600" />
                    Actualización
                  </h4>
                  <div className="text-sm text-gray-600 space-y-2">
                    <div>Última actualización:</div>
                    <div className="font-medium text-gray-900">
                      {new Date().toLocaleString('es-AR')}
                    </div>
                    <div className="text-xs text-gray-500">
                      Los datos se actualizan automáticamente
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                    <BarChart3 className="h-5 w-5 mr-2 text-primary-600" />
                    Cobertura
                  </h4>
                  <div className="text-sm text-gray-600 space-y-2">
                    <div>Zona monitoreada:</div>
                    <div className="font-medium text-gray-900">
                      Gran Tucumán
                    </div>
                    <div className="text-xs text-gray-500">
                      Incluye ciudad y alrededores
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default MapPage