import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { config, apiEndpoints, routes } from '@/lib/config'
import {
  Activity, Target, MapPin, Zap, RefreshCw, AlertTriangle,
  Upload, FileText, TrendingUp, Clock, ImageIcon, CheckCircle2,
  ArrowRight
} from 'lucide-react'
import { StatCard } from '@/components/domain/StatCard'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { Button } from '@/components/ui/Button'
import HeatMap from '@/components/map/HeatMap'
import { useAuthStore } from '@/store/auth'

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

const DashboardPage: React.FC = () => {
  const { user } = useAuthStore()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [userStats, setUserStats] = useState<UserStats | null>(null)
  const [recentAnalyses, setRecentAnalyses] = useState<RecentAnalysis[]>([])
  const [heatMapData, setHeatMapData] = useState<HeatMapDataPoint[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)

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

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-sm text-gray-600">Cargando datos del dashboard...</p>
        </div>
      </div>
    )
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

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Mapa de Calor */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="mb-6">
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-800">Mapa de Detecciones</h2>
            <p className="text-base leading-relaxed text-gray-700 mt-1">
              Distribución geográfica de criaderos
            </p>
          </div>
          <div className="rounded-xl overflow-hidden border border-gray-200">
            <HeatMap
              data={heatMapData}
              center={[-26.8083, -65.2176]}
              zoom={13}
              className="h-96 w-full"
            />
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
