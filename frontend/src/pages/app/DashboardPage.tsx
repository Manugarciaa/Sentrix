import React, { useState, useEffect } from 'react'
import { config, apiEndpoints } from '@/lib/config'
import { showToast } from '@/lib/toast'
import {
  Activity, Target, MapPin, Zap, RefreshCw, AlertTriangle, TrendingUp
} from 'lucide-react'
import { SkeletonDashboard } from '@/components/ui/custom-skeletons'
import { Button } from '@/components/ui/Button'
import HeatMap from '@/components/map/HeatMap'
import { AreaChart, Area, XAxis, YAxis, ResponsiveContainer, Tooltip, PieChart, Pie, Cell } from 'recharts'

interface DashboardStats {
  total_analyses: number
  total_detections: number
  locations_with_gps: number
  model_accuracy: number
  active_zones: number
  total_area_detected_m2?: number
  risk_distribution: {
    bajo: number
    medio: number
    alto: number
    critico: number
  }
  detection_types?: {
    name: string
    value: number
  }[]
  weekly_trend?: {
    day: string
    detections: number
  }[]
}

interface HeatMapDataPoint {
  latitude: number
  longitude: number
  intensity: number
  riskLevel: 'ALTO' | 'MEDIO' | 'BAJO'
  detectionCount: number
  breedingSiteType?: string | null
  location?: string
  timestamp?: string
  isOwn?: boolean
}

const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [heatMapData, setHeatMapData] = useState<HeatMapDataPoint[]>([])

  // Separate loading states for each section
  const [isLoadingStats, setIsLoadingStats] = useState(true)
  const [isLoadingHeatmap, setIsLoadingHeatmap] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)

  // Visualization mode for heatmap
  const [visualizationMode, setVisualizationMode] = useState<'risk-level' | 'breeding-type'>('risk-level')

  const fetchData = async () => {
    try {
      setIsRefreshing(true)
      setIsLoadingStats(true)
      setIsLoadingHeatmap(true)

      // Fetch stats
      const statsPromise = fetch(`${config.api.baseUrl}${apiEndpoints.analyses.mapStats}`)
        .then(async (response) => {
          if (response.ok) {
            const statsData = await response.json()
            setStats(statsData)
          }
          setIsLoadingStats(false)
        })
        .catch((error) => {
          console.error('Error fetching stats:', error)
          setIsLoadingStats(false)
        })

      // Fetch heatmap
      const heatmapPromise = fetch(`${config.api.baseUrl}${apiEndpoints.analyses.heatmapData}`)
        .then(async (response) => {
          if (response.ok) {
            const heatmapData = await response.json()
            const rawData = heatmapData.data || []

            // Para modo breeding-type: mantener solo el tipo predominante por ubicación
            // Para evitar que se superpongan colores en la misma coordenada
            const locationMap = new Map<string, HeatMapDataPoint>()

            rawData.forEach((point: HeatMapDataPoint) => {
              const key = `${point.latitude.toFixed(6)},${point.longitude.toFixed(6)}`
              const existing = locationMap.get(key)

              // Si no existe o el nuevo punto tiene más detecciones, reemplazarlo
              if (!existing || point.detectionCount > existing.detectionCount) {
                locationMap.set(key, point)
              }
            })

            const finalData = Array.from(locationMap.values())
            setHeatMapData(finalData)
          }
          setIsLoadingHeatmap(false)
        })
        .catch((error) => {
          console.error('Error fetching heatmap:', error)
          setIsLoadingHeatmap(false)
        })

      await Promise.all([statsPromise, heatmapPromise])
    } catch (error) {
      console.error('Error fetching data:', error)
      showToast.error('Error al cargar datos', 'No se pudieron obtener las estadísticas')
    } finally {
      setIsRefreshing(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const riskData = stats ? [
    { name: 'Bajo', value: stats.risk_distribution.bajo, color: 'hsl(var(--status-success-bg))' },
    { name: 'Medio', value: stats.risk_distribution.medio, color: 'hsl(var(--status-warning-bg))' },
    { name: 'Alto', value: stats.risk_distribution.alto, color: 'hsl(var(--status-danger-bg))' },
    { name: 'Crítico', value: stats.risk_distribution.critico, color: 'hsl(var(--status-critical-bg))' },
  ] : []

  const totalDetections = riskData.reduce((sum, r) => sum + r.value, 0)

  const COLORS = [
    'hsl(var(--chart-1))',
    'hsl(var(--chart-2))',
    'hsl(var(--chart-3))',
    'hsl(var(--chart-4))',
    'hsl(var(--chart-5))'
  ]
  const detectionTypesData = stats?.detection_types?.map((item, index) => ({
    ...item,
    color: COLORS[index % COLORS.length]
  })) || []

  const weeklyTrendData = stats?.weekly_trend || []

  return (
    <div className="space-y-4 pb-12">
      {/* Header - Responsive */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 py-2">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-xs sm:text-sm text-muted-foreground">
            Monitoreo de detecciones de Aedes aegypti
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={fetchData}
          disabled={isRefreshing}
          className="gap-2 h-8 w-full sm:w-auto"
        >
          <RefreshCw className={`h-3 w-3 ${isRefreshing ? 'animate-spin' : ''}`} />
          <span className="text-xs">{isRefreshing ? 'Actualizando...' : 'Actualizar'}</span>
        </Button>
      </div>

      {/* Main Content - Responsive Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Left Column - Stats & Charts */}
        <div className="space-y-4 md:col-span-2 lg:col-span-1">
          {/* Stats Card */}
          <div className="bg-card border border-border rounded-lg p-3 shadow-sm">
            <h2 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
              <Target className="h-4 w-4 text-primary" />
              Estadísticas
            </h2>
            {isLoadingStats ? (
              // Skeleton para stats
              <div className="space-y-2">
                {[1, 2, 3, 4, 5, 6].map((i) => (
                  <div key={i} className="flex items-center justify-between py-2 border-b border-border/50">
                    <div className="h-3 bg-muted rounded w-24 animate-pulse"></div>
                    <div className="h-4 bg-muted rounded w-10 animate-pulse"></div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-2">
                {/* Análisis */}
                <div className="flex items-center justify-between py-2 border-b border-border/50">
                  <span className="text-sm text-muted-foreground">Análisis</span>
                  <span className="text-base font-semibold text-foreground">{stats?.total_analyses || 0}</span>
                </div>

                {/* Detecciones */}
                <div className="flex items-center justify-between py-2 border-b border-border/50">
                  <span className="text-sm text-muted-foreground">Detecciones</span>
                  <span className="text-base font-semibold text-foreground">{stats?.total_detections || 0}</span>
                </div>

                {/* Zonas Activas */}
                <div className="flex items-center justify-between py-2 border-b border-border/50">
                  <span className="text-sm text-muted-foreground">Zonas Activas</span>
                  <span className="text-base font-semibold text-foreground">{stats?.active_zones || 0}</span>
                </div>

                {/* Con GPS */}
                <div className="flex items-center justify-between py-2 border-b border-border/50">
                  <span className="text-sm text-muted-foreground">Con GPS</span>
                  <span className="text-base font-semibold text-foreground">{stats?.locations_with_gps || 0}</span>
                </div>

                {/* Área Total */}
                <div className="flex items-center justify-between py-2 border-b border-border/50">
                  <span className="text-sm text-muted-foreground">Área Total</span>
                  <span className="text-base font-semibold text-foreground">
                    {stats?.total_area_detected_m2
                      ? `${(stats.total_area_detected_m2 / 1000000).toFixed(1)}km²`
                      : '0km²'
                    }
                  </span>
                </div>

                {/* Precisión IA */}
                <div className="flex items-center justify-between py-2">
                  <span className="text-sm text-muted-foreground">Precisión IA</span>
                  <span className="text-base font-semibold text-foreground">{stats?.model_accuracy || 0}%</span>
                </div>
              </div>
            )}
          </div>

          {/* Distribución de Riesgo */}
          <div className="bg-card border border-border rounded-lg p-3 shadow-sm">
            <h2 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-primary" />
              Distribución de Riesgo
            </h2>
            <div className="space-y-2">
              {isLoadingStats ? (
                // Skeleton para barras de riesgo
                <>
                  {[1, 2, 3, 4].map((i) => (
                    <div key={i}>
                      <div className="flex items-center justify-between mb-1.5">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full bg-muted animate-pulse"></div>
                          <div className="h-4 bg-muted rounded w-16 animate-pulse"></div>
                        </div>
                        <div className="h-4 bg-muted rounded w-8 animate-pulse"></div>
                      </div>
                      <div className="w-full h-2.5 bg-muted rounded-full animate-pulse"></div>
                    </div>
                  ))}
                </>
              ) : (
                riskData.map((item, index) => {
                  const percentage = totalDetections > 0 ? ((item.value / totalDetections) * 100) : 0
                  // Minimum width of 3% when there's data (value > 0) to make it visible
                  const displayWidth = item.value > 0 ? Math.max(percentage, 3) : 0
                  return (
                    <div key={index}>
                      <div className="flex items-center justify-between mb-1.5">
                        <div className="flex items-center gap-2">
                          <div
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: item.color }}
                          />
                          <span className="text-sm font-medium text-foreground">{item.name}</span>
                        </div>
                        <span className="text-sm font-semibold" style={{ color: item.color }}>
                          {item.value}
                        </span>
                      </div>
                      <div className="w-full h-2.5 bg-muted/50 rounded-full overflow-hidden border border-border/30">
                        {displayWidth > 0 && (
                          <div
                            className="h-full rounded-full transition-all duration-500"
                            style={{ width: `${displayWidth}%`, backgroundColor: item.color }}
                          />
                        )}
                      </div>
                    </div>
                  )
                })
              )}
            </div>
          </div>

          {/* Tipos de Detecciones */}
          <div className="bg-card border border-border rounded-lg p-3 shadow-sm">
            <h2 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
              <Activity className="h-4 w-4 text-primary" />
              Tipos de Detecciones
            </h2>
            {isLoadingStats ? (
              // Skeleton para pie chart
              <div className="h-[160px] bg-muted rounded-xl animate-pulse flex items-center justify-center">
                <Activity className="h-8 w-8 text-muted-foreground/30" />
              </div>
            ) : detectionTypesData.length > 0 ? (
              <div className="h-[160px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={detectionTypesData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      outerRadius={65}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {detectionTypesData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'hsl(var(--popover))',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px',
                        padding: '8px 12px',
                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
                      }}
                      itemStyle={{
                        color: 'hsl(var(--popover-foreground))',
                        fontSize: '12px',
                        fontWeight: '500'
                      }}
                      labelStyle={{
                        color: 'hsl(var(--popover-foreground))',
                        fontSize: '12px',
                        fontWeight: '600',
                        marginBottom: '2px'
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-[160px] flex items-center justify-center">
                <div className="text-center">
                  <Activity className="h-8 w-8 text-muted-foreground/30 mx-auto mb-2" />
                  <p className="text-xs text-muted-foreground">Sin datos disponibles</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Column - Map & Trends */}
        <div className="md:col-span-2 lg:col-span-2 space-y-4">
          {/* Mapa de Calor */}
          <div className="bg-card rounded-lg p-3 border border-border shadow-sm">
            {/* Selector de modo de visualización - Responsive */}
            <div className="mb-3 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <h2 className="text-sm font-semibold text-foreground flex items-center gap-2">
                <MapPin className="h-4 w-4 text-primary" />
                Mapa de Detecciones
              </h2>
              <div className="flex gap-1 sm:gap-2 bg-muted/50 p-1 rounded-lg w-full sm:w-auto">
                <button
                  onClick={() => setVisualizationMode('risk-level')}
                  className={`flex-1 sm:flex-none px-2 sm:px-3 py-1.5 text-xs font-medium rounded transition-all ${
                    visualizationMode === 'risk-level'
                      ? 'bg-primary text-primary-foreground shadow-sm'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  Riesgo
                </button>
                <button
                  onClick={() => setVisualizationMode('breeding-type')}
                  className={`flex-1 sm:flex-none px-2 sm:px-3 py-1.5 text-xs font-medium rounded transition-all ${
                    visualizationMode === 'breeding-type'
                      ? 'bg-primary text-primary-foreground shadow-sm'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  Criadero
                </button>
              </div>
            </div>
            <div className="relative h-[350px] sm:h-[400px] md:h-[450px] lg:h-[500px] z-0">
              {isLoadingHeatmap ? (
                // Skeleton para mapa
                <div className="absolute inset-0 bg-muted rounded-xl animate-pulse flex items-center justify-center">
                  <div className="text-center space-y-3">
                    <MapPin className="h-12 w-12 text-muted-foreground/40 mx-auto animate-pulse" />
                    <p className="text-sm text-muted-foreground">Cargando mapa...</p>
                  </div>
                </div>
              ) : (
                <>
                  <HeatMap
                    data={heatMapData}
                    center={[-26.8083, -65.2176]}
                    zoom={13}
                    className="h-full w-full rounded-xl overflow-hidden"
                    visualizationMode={visualizationMode}
                  />
                  {/* Leyenda para modo breeding-type - Responsive */}
                  {visualizationMode === 'breeding-type' && heatMapData.length > 0 && (
                    <div className="absolute bottom-2 left-2 sm:bottom-4 sm:left-4 bg-card/80 backdrop-blur-sm rounded-lg p-2 sm:p-3 shadow-lg border border-primary/15 z-[1000] max-w-[180px] sm:max-w-[200px]">
                      <h4 className="text-[10px] sm:text-xs font-semibold text-foreground/90 mb-1.5 sm:mb-2">Tipos de Criadero</h4>
                      <div className="space-y-1 sm:space-y-1.5">
                        <div className="flex items-center gap-1.5 sm:gap-2">
                          <div className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full flex-shrink-0" style={{ backgroundColor: '#FF8C00' }}></div>
                          <span className="text-[10px] sm:text-xs text-muted-foreground">Basura</span>
                        </div>
                        <div className="flex items-center gap-1.5 sm:gap-2">
                          <div className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full flex-shrink-0" style={{ backgroundColor: '#0064FF' }}></div>
                          <span className="text-[10px] sm:text-xs text-muted-foreground">Charcos/Agua</span>
                        </div>
                        <div className="flex items-center gap-1.5 sm:gap-2">
                          <div className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full flex-shrink-0" style={{ backgroundColor: '#00C800' }}></div>
                          <span className="text-[10px] sm:text-xs text-muted-foreground">Huecos</span>
                        </div>
                        <div className="flex items-center gap-1.5 sm:gap-2">
                          <div className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full flex-shrink-0" style={{ backgroundColor: '#A9A9A9' }}></div>
                          <span className="text-[10px] sm:text-xs text-muted-foreground">Calles</span>
                        </div>
                      </div>
                    </div>
                  )}
                  {heatMapData.length === 0 && !isLoadingHeatmap && (
                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-[5]">
                      <div className="bg-card/70 backdrop-blur-sm rounded-2xl p-6 sm:p-8 shadow-xl border border-primary/15 max-w-md mx-4 transition-all duration-300">
                        <div className="rounded-full p-4 w-20 h-20 mx-auto mb-5 flex items-center justify-center bg-primary/8">
                          <MapPin className="h-10 w-10 text-primary/70" />
                        </div>
                        <h3 className="text-xl font-bold text-foreground/90 mb-3 text-center">
                          Sin datos disponibles
                        </h3>
                        <p className="text-sm text-muted-foreground/80 text-center leading-relaxed">
                          Aún no hay detecciones registradas con ubicación GPS. Las zonas aparecerán aquí
                          cuando se procesen análisis con coordenadas.
                        </p>
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>

          {/* Tendencia Semanal */}
          <div className="bg-card border border-border rounded-lg p-3 shadow-sm">
            <h2 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-primary" />
              Tendencia Semanal
            </h2>
            <div className="h-[200px]">
              {isLoadingStats ? (
                // Skeleton para gráfica
                <div className="h-full bg-muted rounded-xl animate-pulse flex items-center justify-center">
                  <TrendingUp className="h-10 w-10 text-muted-foreground/30" />
                </div>
              ) : weeklyTrendData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={weeklyTrendData}>
                    <defs>
                      <linearGradient id="colorDetections" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis
                      dataKey="day"
                      axisLine={false}
                      tickLine={false}
                      fontSize={12}
                      tick={{ fill: 'hsl(var(--muted-foreground))' }}
                    />
                    <YAxis
                      axisLine={false}
                      tickLine={false}
                      fontSize={12}
                      tick={{ fill: 'hsl(var(--muted-foreground))' }}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'hsl(var(--card))',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '6px',
                        fontSize: '12px'
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="detections"
                      stroke="hsl(var(--primary))"
                      strokeWidth={2}
                      fillOpacity={1}
                      fill="url(#colorDetections)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center">
                  <div className="text-center">
                    <TrendingUp className="h-10 w-10 text-muted-foreground/30 mx-auto mb-2" />
                    <p className="text-sm text-muted-foreground">Sin datos de tendencias</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Alerta de zonas críticas */}
      {stats && stats.risk_distribution.critico > 0 && (
        <div className="critical-alert-panel">
          <div className="flex items-start gap-3">
            <AlertTriangle className="critical-alert-icon" />
            <div>
              <h4 className="text-sm font-semibold text-foreground">Zonas Críticas Detectadas</h4>
              <p className="text-sm text-muted-foreground mt-1">
                Se identificaron <span className="critical-alert-count">{stats.risk_distribution.critico} zonas</span> con nivel crítico que requieren intervención inmediata.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default DashboardPage
