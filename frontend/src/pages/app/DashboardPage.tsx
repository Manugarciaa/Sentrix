import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { config, apiEndpoints, routes } from '@/lib/config'
import {
  Activity, Target, MapPin, Zap, RefreshCw, AlertTriangle,
  Upload, FileText, TrendingUp, TrendingDown, Minus, Clock, ImageIcon, CheckCircle2,
  ArrowRight, Image, Layers
} from 'lucide-react'
import { StatCard } from '@/components/domain/StatCard'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { Button } from '@/components/ui/Button'
import HeatMap from '@/components/map/HeatMap'
import { useAuthStore } from '@/store/auth'
import { AreaChart, Area, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts'

interface DashboardStats {
  total_analyses: number
  total_detections: number
  area_monitored_km2: number
  model_accuracy: number
  active_zones: number
  risk_distribution: {
    bajo: number
    medio: number
    alto: number
    critico: number
  }
}

interface HeatMapDataPoint {
  latitude: number
  longitude: number
  intensity: number
  riskLevel: 'ALTO' | 'MEDIO' | 'BAJO'
  detectionCount: number
}

interface RecentAnalysis {
  id: string
  image_url: string
  status: string
  detections_count: number
  created_at: string
  risk_level?: string
}

interface UserStats {
  total_analyses: number
  total_detections: number
  pending_analyses: number
  completed_analyses: number
}

interface TrendData {
  day: string
  detections: number
}

interface StatWithTrend {
  label: string
  value: string
  trend: { value: number; direction: 'up' | 'down' | 'neutral' }
  icon?: string
  trendData?: TrendData[]
  description?: string
}

const DashboardPage: React.FC = () => {
  const { user } = useAuthStore()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [userStats, setUserStats] = useState<UserStats | null>(null)
  const [recentAnalyses, setRecentAnalyses] = useState<RecentAnalysis[]>([])
  const [heatMapData, setHeatMapData] = useState<HeatMapDataPoint[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [visualizationMode, setVisualizationMode] = useState<'risk-level' | 'breeding-type'>('risk-level')

  // Datos mock para demostración de tendencias
  const mockTrendData: TrendData[] = [
    { day: 'Lun', detections: 45 },
    { day: 'Mar', detections: 52 },
    { day: 'Mié', detections: 48 },
    { day: 'Jue', detections: 65 },
    { day: 'Vie', detections: 72 },
    { day: 'Sáb', detections: 68 },
    { day: 'Dom', detections: 58 }
  ]

  const fetchData = async () => {
    try {
      setIsRefreshing(true)

      // Fetch all data in parallel
      const [statsResponse, heatmapResponse, analysesResponse] = await Promise.all([
        fetch(`${config.api.baseUrl}${apiEndpoints.analyses.mapStats}`),
        fetch(`${config.api.baseUrl}${apiEndpoints.analyses.heatmapData}`),
        fetch(`${config.api.baseUrl}${apiEndpoints.analyses.list}?limit=3`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        })
      ])

      if (statsResponse.ok) {
        const statsData = await statsResponse.json()
        setStats(statsData)
      }

      if (heatmapResponse.ok) {
        const heatmapData = await heatmapResponse.json()
        setHeatMapData(heatmapData.data || [])
      }

      if (analysesResponse.ok) {
        const analysesData = await analysesResponse.json()
        setRecentAnalyses(analysesData.analyses?.slice(0, 3) || [])

        // Calculate user stats from analyses
        if (analysesData.analyses) {
          const userAnalyses = analysesData.analyses
          setUserStats({
            total_analyses: userAnalyses.length,
            total_detections: userAnalyses.reduce((sum: number, a: any) => sum + (a.detections_count || 0), 0),
            pending_analyses: userAnalyses.filter((a: any) => a.status === 'pending').length,
            completed_analyses: userAnalyses.filter((a: any) => a.status === 'completed').length
          })
        }
      }
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setIsLoading(false)
      setIsRefreshing(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const riskData = stats ? [
    { name: 'Bajo', value: stats.risk_distribution.bajo, color: '#9ca3af', bgColor: 'bg-gray-50', textColor: 'text-gray-700' },
    { name: 'Medio', value: stats.risk_distribution.medio, color: '#9ca3af', bgColor: 'bg-gray-50', textColor: 'text-gray-700' },
    { name: 'Alto', value: stats.risk_distribution.alto, color: '#9ca3af', bgColor: 'bg-gray-50', textColor: 'text-gray-700' },
    { name: 'Crítico', value: stats.risk_distribution.critico, color: '#6b7280', bgColor: 'bg-gray-50', textColor: 'text-gray-900' },
  ] : []

  const totalDetections = riskData.reduce((sum, r) => sum + r.value, 0)
  const activeZones = heatMapData.length

  // Estadísticas con tendencias para usuarios autenticados
  const statsWithTrends: StatWithTrend[] = [
    {
      label: 'Criaderos Detectados',
      value: stats?.total_detections?.toString() || totalDetections.toString(),
      trend: { value: 12, direction: 'up' },
      trendData: mockTrendData,
      description: 'Detecciones confirmadas por IA'
    },
    {
      label: 'Imágenes Procesadas',
      value: stats?.total_analyses?.toLocaleString() || '0',
      trend: { value: 8, direction: 'up' },
      icon: 'Image'
    },
    {
      label: 'Precisión del Modelo',
      value: `${stats?.model_accuracy || 0}%`,
      trend: { value: 2, direction: 'up' },
      icon: 'Target'
    },
    {
      label: 'Zonas Monitoreadas',
      value: (stats?.active_zones || activeZones).toString(),
      trend: { value: 0, direction: 'neutral' },
      icon: 'MapPin'
    }
  ]

  // Separar card principal de las secundarias
  const mainStat = statsWithTrends[0]
  const secondaryStats = statsWithTrends.slice(1)

  // Función para obtener ícono de tendencia
  const getTrendIcon = (direction: 'up' | 'down' | 'neutral') => {
    switch (direction) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-green-600" />
      case 'down':
        return <TrendingDown className="h-4 w-4 text-red-600" />
      case 'neutral':
        return <Minus className="h-4 w-4 text-gray-500" />
    }
  }

  // Función para obtener color de tendencia
  const getTrendColor = (direction: 'up' | 'down' | 'neutral') => {
    switch (direction) {
      case 'up':
        return 'text-green-600'
      case 'down':
        return 'text-red-600'
      case 'neutral':
        return 'text-gray-500'
    }
  }

  // Función para obtener ícono por nombre
  const getStatIcon = (iconName: string) => {
    switch (iconName) {
      case 'Image':
        return <Image className="h-6 w-6 text-primary-600" />
      case 'Target':
        return <Target className="h-6 w-6 text-primary-600" />
      case 'MapPin':
        return <MapPin className="h-6 w-6 text-primary-600" />
      default:
        return null
    }
  }

  return (
    <div className="space-y-6 sm:space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-3">
        <div>
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-sm sm:text-base text-gray-600 mt-1.5">
            Resumen general del sistema
          </p>
        </div>
        <div className="flex flex-col sm:flex-row sm:items-center gap-3">
          <span className="text-xs sm:text-sm text-gray-500">
            Actualizado: {new Date().toLocaleDateString('es-ES', {
              day: '2-digit',
              month: 'short',
              hour: '2-digit',
              minute: '2-digit'
            })}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchData}
            disabled={isRefreshing}
            className="gap-2 w-full sm:w-auto"
          >
            <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            Actualizar
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-lg transition-all">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-medium text-gray-600">Análisis Totales</h4>
            <Activity className="h-5 w-5 text-gray-400" />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {stats?.total_analyses || 0}
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-lg transition-all">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-medium text-gray-600">Detecciones</h4>
            <Target className="h-5 w-5 text-gray-400" />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {stats?.total_detections || 0}
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-lg transition-all">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-medium text-gray-600">Zonas Activas</h4>
            <MapPin className="h-5 w-5 text-gray-400" />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {stats?.active_zones || 0}
          </p>
          <p className="text-sm text-gray-600 mt-1">{stats?.area_monitored_km2 || 0} km²</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-lg transition-all">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-medium text-gray-600">Precisión IA</h4>
            <Zap className="h-5 w-5 text-gray-400" />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {stats?.model_accuracy || 0}%
          </p>
        </div>
      </div>

      {/* Resultados del Sistema - Sección con Tendencias */}
      <div>
        <div className="mb-6">
          <h2 className="text-2xl sm:text-3xl font-bold text-gray-800">Resultados del Sistema</h2>
          <p className="text-sm sm:text-base text-gray-600 mt-1">
            Métricas de rendimiento y tendencias semanales
          </p>
        </div>

        {/* Layout asimétrico */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
          {/* Card Principal - 2 columnas */}
          <div className="lg:col-span-2">
            <div className="group p-6 sm:p-8 rounded-2xl bg-gradient-to-br from-primary-50 to-white border border-gray-200 hover:border-primary-200 hover:shadow-lg transition-all duration-500">
              {/* Header de la card principal */}
              <div className="flex items-start justify-between mb-4 sm:mb-6 gap-2">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-1 sm:mb-2">
                    {mainStat.label}
                  </h3>
                  <p className="text-sm leading-normal text-gray-600">
                    {mainStat.description}
                  </p>
                </div>
                {/* Indicador de tendencia principal */}
                <div className={`flex items-center space-x-1 px-2 sm:px-3 py-1 rounded-full bg-white/80 ${getTrendColor(mainStat.trend.direction)} flex-shrink-0`}>
                  {getTrendIcon(mainStat.trend.direction)}
                  <span className="text-xs sm:text-sm font-medium">
                    {mainStat.trend.value > 0 ? '+' : ''}{mainStat.trend.value}%
                  </span>
                </div>
              </div>

              {/* Número destacado */}
              <div className="text-5xl sm:text-6xl lg:text-7xl font-bold text-primary-600 mb-4 sm:mb-6 group-hover:scale-105 transition-transform duration-300">
                {mainStat.value}
              </div>

              {/* Gráfico de tendencia semanal */}
              {mainStat.trendData && (
                <div className="mt-4 sm:mt-6">
                  <h4 className="text-lg font-semibold text-gray-900 mb-2 sm:mb-3">Tendencia semanal</h4>
                  <div className="h-24 sm:h-32">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={mainStat.trendData}>
                        <defs>
                          <linearGradient id="colorDetections" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="rgb(0 188 212)" stopOpacity={0.4} />
                            <stop offset="95%" stopColor="rgb(0 188 212)" stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <XAxis
                          dataKey="day"
                          axisLine={false}
                          tickLine={false}
                          fontSize={10}
                          tick={{ fill: '#6b7280' }}
                        />
                        <YAxis hide />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: 'white',
                            border: '1px solid #e5e7eb',
                            borderRadius: '8px',
                            fontSize: '11px'
                          }}
                          labelStyle={{ color: '#374151' }}
                        />
                        <Area
                          type="monotone"
                          dataKey="detections"
                          stroke="rgb(0 188 212)"
                          strokeWidth={2}
                          fillOpacity={1}
                          fill="url(#colorDetections)"
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="flex justify-between text-[10px] sm:text-xs text-gray-500 mt-1 sm:mt-2">
                    <span>Detecciones diarias</span>
                    <span className={getTrendColor(mainStat.trend.direction)}>
                      vs semana anterior
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Cards Secundarias - 1 columna */}
          <div className="space-y-4 sm:space-y-6">
            {secondaryStats.map((stat, index) => (
              <div
                key={index}
                className="group p-6 rounded-xl bg-stone-50 border border-gray-200 hover:border-primary-200 hover:shadow-sm hover:-translate-y-1 transition-all duration-300"
              >
                {/* Header con ícono */}
                <div className="flex items-center justify-between mb-3 sm:mb-4">
                  <div className="flex items-center space-x-2 sm:space-x-3">
                    {stat.icon && getStatIcon(stat.icon)}
                    <h3 className="text-lg font-semibold text-gray-900">
                      {stat.label}
                    </h3>
                  </div>
                  {/* Mini indicador de tendencia */}
                  <div className="flex items-center space-x-1">
                    {getTrendIcon(stat.trend.direction)}
                    <span className={`text-[10px] sm:text-xs font-medium ${getTrendColor(stat.trend.direction)}`}>
                      {stat.trend.value > 0 ? '+' : ''}{stat.trend.value}%
                    </span>
                  </div>
                </div>

                {/* Número */}
                <div className="text-2xl sm:text-3xl lg:text-4xl font-bold text-primary-600 group-hover:scale-105 transition-transform duration-300">
                  {stat.value}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Mapa de Calor */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="mb-6">
            <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-3 mb-2">
              <div>
                <h2 className="text-2xl sm:text-3xl font-bold text-gray-800">Mapa de Detecciones</h2>
                <p className="text-base leading-relaxed text-gray-700 mt-1">
                  Distribución geográfica de criaderos
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant={visualizationMode === 'risk-level' ? 'primary' : 'outline'}
                  size="sm"
                  onClick={() => setVisualizationMode('risk-level')}
                  className="gap-2"
                >
                  <Layers className="h-4 w-4" />
                  Por Riesgo
                </Button>
                <Button
                  variant={visualizationMode === 'breeding-type' ? 'primary' : 'outline'}
                  size="sm"
                  onClick={() => setVisualizationMode('breeding-type')}
                  className="gap-2"
                >
                  <Layers className="h-4 w-4" />
                  Por Tipo
                </Button>
              </div>
            </div>
          </div>
          <div className="rounded-xl overflow-hidden border border-gray-200 relative">
            <HeatMap
              data={heatMapData}
              center={[-26.8083, -65.2176]}
              zoom={13}
              className="h-96 w-full"
              visualizationMode={visualizationMode}
            />
            {heatMapData.length === 0 && !isLoading && (
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="bg-white/95 backdrop-blur-sm rounded-xl p-6 shadow-lg border border-gray-200 max-w-md mx-4">
                  <MapPin className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2 text-center">
                    Sin Detecciones Registradas
                  </h3>
                  <p className="text-sm text-gray-600 text-center">
                    No hay detecciones con coordenadas GPS disponibles. Sube imágenes con metadatos de ubicación para ver el mapa de calor.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Risk Distribution */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="mb-6">
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-800">Distribución</h2>
            <p className="text-base leading-relaxed text-gray-700 mt-1">Por nivel de riesgo</p>
          </div>
          <div className="space-y-4">
            {riskData.map((item, index) => {
              const percentage = totalDetections > 0 ? ((item.value / totalDetections) * 100).toFixed(0) : 0
              return (
                <div key={index}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-base leading-relaxed text-gray-700 font-medium">{item.name}</span>
                    <span className="text-lg font-semibold text-gray-900">{item.value}</span>
                  </div>
                  <div className="relative w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="absolute top-0 left-0 h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${percentage}%`,
                        backgroundColor: item.color
                      }}
                    />
                  </div>
                  <p className="text-sm leading-normal text-gray-600 mt-1">{percentage}% del total</p>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Alertas o información adicional */}
      {stats && stats.risk_distribution.critico > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0">
              <AlertTriangle className="h-5 w-5 text-gray-600" />
            </div>
            <div>
              <h4 className="text-lg font-semibold text-gray-900">
                Atención: Zonas Críticas Detectadas
              </h4>
              <p className="text-base leading-relaxed text-gray-700 mt-2">
                Se han identificado <strong>{stats.risk_distribution.critico}</strong> zonas con nivel de riesgo crítico.
                Se recomienda tomar acciones inmediatas de control y mitigación.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default DashboardPage
