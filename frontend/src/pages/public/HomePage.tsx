import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { routes, config, apiEndpoints } from '@/lib/config'
import { ArrowRight, CheckCircle, Target, TrendingUp, TrendingDown, Minus, Image, MapPin, Zap, Search } from 'lucide-react'
import HeatMap from '@/components/map/HeatMap'
import { AreaChart, Area, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts'

interface MapStats {
  total_analyses: number
  total_detections: number
  area_monitored_km2: number
  model_accuracy: number
  last_updated: string
  risk_distribution: {
    bajo: number
    medio: number
    alto: number
    critico: number
  }
  active_zones?: number
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

const HomePage: React.FC = () => {
  const [heatMapData, setHeatMapData] = useState<any[]>([])
  const [mapStats, setMapStats] = useState<MapStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)

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

  // Fetch real data from backend
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch both heatmap data and statistics in parallel
        const [heatmapResponse, statsResponse] = await Promise.all([
          fetch(`${config.api.baseUrl}${apiEndpoints.analyses.heatmapData}`),
          fetch(`${config.api.baseUrl}${apiEndpoints.analyses.mapStats}`)
        ])

        if (heatmapResponse.ok) {
          const heatmapResponse_data = await heatmapResponse.json()
          setHeatMapData(heatmapResponse_data.data || [])
        }

        if (statsResponse.ok) {
          const statsData = await statsResponse.json()
          setMapStats(statsData)
        }
      } catch (error) {
        console.error('Error fetching map data:', error)
        // Keep loading state or show fallback data
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [])

  // Generar estadísticas con tendencias
  const statsWithTrends: StatWithTrend[] = mapStats ? [
    {
      label: 'Criaderos Detectados',
      value: mapStats.total_detections.toString(),
      trend: { value: 15, direction: 'up' },
      trendData: mockTrendData,
      description: 'Detecciones confirmadas por IA'
    },
    {
      label: 'Imágenes Procesadas',
      value: mapStats.total_analyses.toLocaleString(),
      trend: { value: 8, direction: 'up' },
      icon: 'Image'
    },
    {
      label: 'Precisión del Modelo',
      value: `${mapStats.model_accuracy}%`,
      trend: { value: 2, direction: 'up' },
      icon: 'Target'
    },
    {
      label: 'Zonas Monitoreadas',
      value: (mapStats.active_zones || 0).toString(),
      trend: { value: 0, direction: 'neutral' },
      icon: 'MapPin'
    }
  ] : [
    {
      label: 'Criaderos Detectados',
      value: '342',
      trend: { value: 15, direction: 'up' },
      trendData: mockTrendData,
      description: 'Detecciones confirmadas por IA'
    },
    {
      label: 'Imágenes Procesadas',
      value: '1,247',
      trend: { value: 8, direction: 'up' },
      icon: 'Image'
    },
    {
      label: 'Precisión del Modelo',
      value: '87.3%',
      trend: { value: 2, direction: 'up' },
      icon: 'Target'
    },
    {
      label: 'Zonas Monitoreadas',
      value: '23',
      trend: { value: 0, direction: 'neutral' },
      icon: 'MapPin'
    }
  ]

  // Separar card principal de las secundarias
  const mainStat = statsWithTrends[0] // Criaderos Detectados
  const secondaryStats = statsWithTrends.slice(1) // Las otras 3

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
    <div className="flex flex-col">
      {/* Hero Section - Clean Minimalist */}
      <section className="relative bg-gradient-to-br from-primary-50 via-blue-50 to-cyan-50 overflow-hidden">
        <div className="relative mx-auto max-w-6xl px-4 py-24 sm:px-6 lg:px-8 lg:py-32">
          <div className="text-center">
            <div className="inline-flex items-center rounded-full bg-white/90 backdrop-blur-sm shadow-sm border border-primary-200 px-6 py-2 text-sm font-medium text-primary-700 mb-8">
              <CheckCircle className="h-4 w-4 mr-2" />
              Proyecto de Tesis - UNSTA 2025
            </div>

            <h1 className="text-5xl font-bold tracking-tight text-gray-900 sm:text-6xl lg:text-8xl mb-6">
              <span className="block text-gray-800">Sistema</span>
              <span className="block text-primary-600">
                Sentrix
              </span>
              <span className="block text-3xl sm:text-4xl lg:text-5xl font-medium text-gray-600 mt-2">
                Detección con IA
              </span>
            </h1>

            <p className="mx-auto mt-8 max-w-3xl text-xl text-gray-600 leading-relaxed">
              Sistema experimental de detección automatizada de criaderos de{' '}
              <em className="text-primary-700 font-medium">Aedes aegypti</em>
              <br className="hidden sm:block" />
              mediante modelos YOLOv11, desarrollado como proyecto de investigación académica.
            </p>

            <div className="mt-16 flex flex-col sm:flex-row gap-6 justify-center">
              <Link to={routes.app.dashboard}>
                <Button size="lg" className="group bg-gradient-to-r from-primary-600 to-primary-700 text-white hover:from-primary-700 hover:to-primary-800 px-12 py-6 text-lg font-medium shadow-lg hover:shadow-xl transition-all duration-300 rounded-2xl">
                  <Zap className="mr-3 h-6 w-6 group-hover:scale-110 group-hover:rotate-12 transition-all duration-300" />
                  Acceder al Sistema
                  <ArrowRight className="ml-3 h-5 w-5 group-hover:translate-x-1 transition-transform duration-300" />
                </Button>
              </Link>
              <Link to={routes.public.report}>
                <Button size="lg" variant="outline" className="group border-2 border-primary-300 text-primary-700 hover:bg-primary-50 hover:border-primary-400 hover:text-primary-800 px-12 py-6 text-lg font-medium shadow-md hover:shadow-lg transition-all duration-300 bg-white/90 backdrop-blur-sm rounded-2xl">
                  <Search className="mr-3 h-6 w-6 group-hover:scale-110 group-hover:rotate-12 transition-all duration-300" />
                  Probar Detección
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section - Layout Asimétrico */}
      <section className="bg-gradient-to-b from-cyan-50 to-white py-20">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          {/* Título existente - mantener igual */}
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-800 mb-4">
              Resultados del Sistema
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Métricas de rendimiento y detecciones procesadas hasta la fecha
            </p>
          </div>

          {/* Layout asimétrico */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Card Principal - 2 columnas */}
            <div className="lg:col-span-2">
              <div className="group p-8 rounded-3xl bg-gradient-to-br from-primary-50 to-white border border-stone-200 hover:border-primary-200 hover:shadow-xl transition-all duration-500">
                {/* Header de la card principal */}
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 mb-2">
                      {mainStat.label}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {mainStat.description}
                    </p>
                  </div>
                  {/* Indicador de tendencia principal */}
                  <div className={`flex items-center space-x-1 px-3 py-1 rounded-full bg-white/80 ${getTrendColor(mainStat.trend.direction)}`}>
                    {getTrendIcon(mainStat.trend.direction)}
                    <span className="text-sm font-medium">
                      {mainStat.trend.value > 0 ? '+' : ''}{mainStat.trend.value}%
                    </span>
                  </div>
                </div>

                {/* Número destacado */}
                <div className="text-6xl lg:text-7xl font-bold text-primary-600 mb-6 group-hover:scale-105 transition-transform duration-300">
                  {mainStat.value}
                </div>

                {/* Gráfico de tendencia semanal */}
                {mainStat.trendData && (
                  <div className="mt-6">
                    <h4 className="text-sm font-medium text-gray-700 mb-3">Tendencia semanal</h4>
                    <div className="h-32">
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
                            fontSize={12}
                            tick={{ fill: '#6b7280' }}
                          />
                          <YAxis hide />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: 'white',
                              border: '1px solid #e5e7eb',
                              borderRadius: '8px',
                              fontSize: '12px'
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
                    <div className="flex justify-between text-xs text-gray-500 mt-2">
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
            <div className="space-y-6">
              {secondaryStats.map((stat, index) => (
                <div
                  key={index}
                  className="group p-6 rounded-2xl bg-stone-50 border border-stone-200 hover:border-primary-200 hover:shadow-lg hover:-translate-y-1 transition-all duration-300"
                >
                  {/* Header con ícono */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      {stat.icon && getStatIcon(stat.icon)}
                      <h3 className="text-sm font-semibold text-gray-900">
                        {stat.label}
                      </h3>
                    </div>
                    {/* Mini indicador de tendencia */}
                    <div className="flex items-center space-x-1">
                      {getTrendIcon(stat.trend.direction)}
                      <span className={`text-xs font-medium ${getTrendColor(stat.trend.direction)}`}>
                        {stat.trend.value > 0 ? '+' : ''}{stat.trend.value}%
                      </span>
                    </div>
                  </div>

                  {/* Número */}
                  <div className="text-3xl lg:text-4xl font-bold text-primary-600 group-hover:scale-105 transition-transform duration-300">
                    {stat.value}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Map & Risk Analysis Section - Integrated */}
      <section className="py-24 bg-stone-50">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          {/* Risk Classification Header */}
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-800 mb-4">
              Niveles de Riesgo
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Clasificación automática basada en densidad de criaderos detectados y factores ambientales
            </p>
          </div>

          {/* Risk Level Cards - Enhanced */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-20">
            {/* Bajo */}
            <div className="group text-center p-6 rounded-2xl bg-gradient-to-br from-green-50 to-emerald-50 border border-stone-200 hover:border-green-200 hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
              <h5 className="text-xl font-bold text-green-700 mb-2 group-hover:scale-105 transition-transform duration-300">Bajo</h5>
              <p className="text-sm text-green-600 mb-4">0-25%</p>
              <p className="text-sm text-gray-600 leading-relaxed mb-4">
                Zona con baja concentración de criaderos. Monitoreo preventivo recomendado.
              </p>
              <div className="flex items-center justify-center text-xs text-green-600 font-medium">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                Riesgo controlado
              </div>
            </div>

            {/* Medio */}
            <div className="group text-center p-6 rounded-2xl bg-gradient-to-br from-yellow-50 to-amber-50 border border-stone-200 hover:border-yellow-200 hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
              <h5 className="text-xl font-bold text-yellow-700 mb-2 group-hover:scale-105 transition-transform duration-300">Medio</h5>
              <p className="text-sm text-yellow-600 mb-4">25-50%</p>
              <p className="text-sm text-gray-600 leading-relaxed mb-4">
                Concentración moderada. Requiere vigilancia activa y medidas preventivas.
              </p>
              <div className="flex items-center justify-center text-xs text-yellow-600 font-medium">
                <div className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></div>
                Vigilancia requerida
              </div>
            </div>

            {/* Alto */}
            <div className="group text-center p-6 rounded-2xl bg-gradient-to-br from-orange-50 to-red-50 border border-stone-200 hover:border-orange-200 hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
              <h5 className="text-xl font-bold text-orange-700 mb-2 group-hover:scale-105 transition-transform duration-300">Alto</h5>
              <p className="text-sm text-orange-600 mb-4">50-75%</p>
              <p className="text-sm text-gray-600 leading-relaxed mb-4">
                Alta densidad de criaderos. Intervención inmediata necesaria.
              </p>
              <div className="flex items-center justify-center text-xs text-orange-600 font-medium">
                <div className="w-2 h-2 bg-orange-500 rounded-full mr-2"></div>
                Acción inmediata
              </div>
            </div>

            {/* Crítico */}
            <div className="group text-center p-6 rounded-2xl bg-gradient-to-br from-red-50 to-pink-50 border border-stone-200 hover:border-red-200 hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
              <h5 className="text-xl font-bold text-red-700 mb-2 group-hover:scale-105 transition-transform duration-300">Crítico</h5>
              <p className="text-sm text-red-600 mb-4">75-100%</p>
              <p className="text-sm text-gray-600 leading-relaxed mb-4">
                Concentración extrema. Alerta sanitaria y control de emergencia.
              </p>
              <div className="flex items-center justify-center text-xs text-red-600 font-medium">
                <div className="w-2 h-2 bg-red-500 rounded-full mr-2"></div>
                Emergencia sanitaria
              </div>
            </div>
          </div>

          {/* Map Section Header */}
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-800 mb-4">
              Mapa de Detecciones
              <span className="block text-primary-600 mt-2">en Tiempo Real</span>
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Visualiza las áreas monitoreadas y los focos de riesgo detectados por el sistema de IA
              en la provincia de Tucumán
            </p>
          </div>

          {/* Map Container - Enhanced */}
          <div className="group bg-white rounded-2xl p-6 shadow-lg border border-stone-200 hover:border-primary-200 hover:shadow-xl transition-all duration-500">
            {isLoading ? (
              /* Clean Loading Placeholder */
              <div className="relative h-96 bg-stone-50 rounded-xl border-2 border-dashed border-stone-300 flex items-center justify-center">
                <div className="text-center">
                  <div className="relative mb-6">
                    <div className="animate-spin h-16 w-16 border-4 border-stone-200 border-t-primary-600 rounded-full mx-auto"></div>
                  </div>
                  <h3 className="text-2xl font-semibold text-gray-800 mb-3">Cargando Mapa de Calor</h3>
                  <p className="text-gray-600 text-lg">
                    Procesando datos de <span className="font-medium text-primary-600">{mapStats?.active_zones || 0}</span> ubicaciones...
                  </p>
                </div>
              </div>
            ) : (
              /* Clean Heat Map */
              <div className="relative">
                <HeatMap
                  data={heatMapData}
                  center={[-26.8083, -65.2176]}
                  zoom={13}
                  className="h-96 w-full rounded-xl overflow-hidden"
                />
                <div className="absolute top-4 right-4 bg-white/95 backdrop-blur-sm rounded-lg px-3 py-2 shadow-md border border-stone-200">
                  <p className="text-sm font-medium text-gray-700">
                    {heatMapData.length} detecciones activas
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  )
}

export default HomePage