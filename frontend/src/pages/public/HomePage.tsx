import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { routes, config, apiEndpoints } from '@/lib/config'
import { ArrowRight, CheckCircle, Target, TrendingUp, TrendingDown, Minus, Image, MapPin } from 'lucide-react'
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

interface HeatMapDataPoint {
  latitude: number
  longitude: number
  intensity: number
  riskLevel: 'ALTO' | 'MEDIO' | 'BAJO'
  detectionCount: number
}

const HomePage: React.FC = () => {
  const [heatMapData, setHeatMapData] = useState<HeatMapDataPoint[]>([])
  const [mapStats, setMapStats] = useState<MapStats | null>(null)
  const [isLoading, setIsLoading] = useState(false)

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

  // Datos de ejemplo para demostración del mapa de calor
  const mockHeatMapData: HeatMapDataPoint[] = [
    {
      latitude: -26.8083,
      longitude: -65.2176,
      intensity: 0.8,
      riskLevel: 'ALTO',
      detectionCount: 15
    },
    {
      latitude: -26.8150,
      longitude: -65.2100,
      intensity: 0.6,
      riskLevel: 'MEDIO',
      detectionCount: 8
    },
    {
      latitude: -26.8000,
      longitude: -65.2250,
      intensity: 0.9,
      riskLevel: 'ALTO',
      detectionCount: 22
    },
    {
      latitude: -26.8200,
      longitude: -65.2050,
      intensity: 0.4,
      riskLevel: 'BAJO',
      detectionCount: 3
    },
    {
      latitude: -26.8120,
      longitude: -65.2300,
      intensity: 0.7,
      riskLevel: 'MEDIO',
      detectionCount: 12
    },
    {
      latitude: -26.8050,
      longitude: -65.2150,
      intensity: 0.95,
      riskLevel: 'ALTO',
      detectionCount: 28
    },
    {
      latitude: -26.8180,
      longitude: -65.2200,
      intensity: 0.3,
      riskLevel: 'BAJO',
      detectionCount: 2
    },
    {
      latitude: -26.8100,
      longitude: -65.2080,
      intensity: 0.85,
      riskLevel: 'ALTO',
      detectionCount: 19
    }
  ]

  // Fetch real data from backend
  useEffect(() => {
    // Inicializar inmediatamente con datos de ejemplo
    setHeatMapData(mockHeatMapData)
    
    const fetchData = async () => {
      try {
        setIsLoading(true)
        // Fetch both heatmap data and statistics in parallel
        const [heatmapResponse, statsResponse] = await Promise.all([
          fetch(`${config.api.baseUrl}${apiEndpoints.analyses.heatmapData}`),
          fetch(`${config.api.baseUrl}${apiEndpoints.analyses.mapStats}`)
        ])

        if (heatmapResponse.ok) {
          const heatmapResponse_data = await heatmapResponse.json()
          setHeatMapData(heatmapResponse_data.data || mockHeatMapData)
        }

        if (statsResponse.ok) {
          const statsData = await statsResponse.json()
          setMapStats(statsData)
        }
      } catch (error) {
        console.error('Error fetching map data:', error)
        // Los datos de ejemplo ya están cargados, no hacer nada
      } finally {
        setIsLoading(false)
      }
    }

    // Ejecutar la carga de datos reales después de un pequeño delay
    setTimeout(fetchData, 100)
  }, [])

  // Generar estadísticas con tendencias

  // Calcular estadísticas basadas en los datos del mapa
  const totalDetections = heatMapData.reduce((sum, point) => sum + point.detectionCount, 0)
  const activeZones = heatMapData.length

  const statsWithTrends: StatWithTrend[] = [
    {
      label: 'Criaderos Detectados',
      value: mapStats?.total_detections?.toString() || totalDetections.toString(),
      trend: { value: 12, direction: 'up' },
      trendData: mapStats?.total_detections ? mockTrendData : mockTrendData,
      description: 'Detecciones confirmadas por IA'
    },
    {
      label: 'Imágenes Procesadas',
      value: mapStats?.total_analyses?.toLocaleString() || '1,247',
      trend: { value: 8, direction: 'up' },
      icon: 'Image'
    },
    {
      label: 'Precisión del Modelo',
      value: `${mapStats?.model_accuracy || 94}%`,
      trend: { value: 2, direction: 'up' },
      icon: 'Target'
    },
    {
      label: 'Zonas Monitoreadas',
      value: (mapStats?.active_zones || activeZones).toString(),
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
      {/* Hero Section - Enhanced */}
      <section className="relative bg-gradient-to-b from-white to-blue-50/30 overflow-hidden min-h-screen flex items-center pt-28 pb-12 sm:pt-32 sm:pb-16">
        <div className="relative mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 w-full">
          <div className="text-center">
            <div className="inline-flex items-center gap-2 rounded-full bg-white/70 backdrop-blur-sm shadow-sm border border-primary-200/50 px-4 sm:px-5 py-1.5 sm:py-2 text-xs font-medium text-primary-700 mb-6 sm:mb-8">
              <CheckCircle className="h-3.5 w-3.5 text-primary-600 flex-shrink-0" />
              <span className="text-xs whitespace-nowrap">Proyecto de Tesis - UNSTA 2025</span>
            </div>

            <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight text-gray-900 font-akira leading-tight mb-6 sm:mb-8">
              Detector de Criaderos<br />
              <span className="text-primary-600">de Dengue con IA</span>
            </h1>

            <p className="mx-auto max-w-2xl text-base leading-relaxed text-gray-700 mb-8 sm:mb-12 px-4">
              Identifica criaderos de Aedes aegypti en tiempo real con tecnología de visión artificial.
            </p>

            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center items-center px-4">
              <Link to={routes.app.dashboard} className="w-full sm:w-auto">
                <Button size="lg" className="group bg-gradient-to-r from-primary-600 to-cyan-600 hover:from-primary-700 hover:to-cyan-700 text-white px-6 sm:px-8 py-4 sm:py-5 text-sm sm:text-base font-medium shadow-lg hover:shadow-xl transition-all rounded-lg w-full sm:w-auto">
                  Acceder al Sistema
                  <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
              <Link to={routes.public.report} className="w-full sm:w-auto">
                <Button size="lg" variant="outline" className="border-2 border-primary-500 text-primary-700 hover:bg-primary-50 px-6 sm:px-8 py-4 sm:py-5 text-sm sm:text-base font-medium transition-all rounded-lg shadow-sm w-full sm:w-auto">
                  Probar Detección
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* El Problema del Dengue */}
      <section className="bg-white py-12 sm:py-16 md:py-24">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12 sm:mb-16">
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-800 mb-3 sm:mb-4">
              El Problema del Dengue
            </h2>
            <p className="text-base leading-relaxed text-gray-700 max-w-3xl mx-auto px-2 text-justify">
              El dengue es una de las enfermedades transmitidas por mosquitos más importantes a nivel mundial,
              causando millones de casos cada año. En Argentina, especialmente en Tucumán y el norte del país,
              representa un desafío constante para la salud pública. La prevención y detección temprana de criaderos
              del mosquito Aedes aegypti son fundamentales para evitar brotes epidémicos que afectan a comunidades enteras.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 sm:gap-8">
            <div className="flex flex-col items-center text-center group p-4 sm:p-0">
              <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2 sm:mb-3">500M+</h3>
              <p className="text-base leading-relaxed text-gray-700">
                casos de dengue a nivel mundial cada año, con un crecimiento constante
              </p>
            </div>

            <div className="flex flex-col items-center text-center group p-4 sm:p-0">
              <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2 sm:mb-3">Aedes aegypti</h3>
              <p className="text-base leading-relaxed text-gray-700">
                El mosquito transmisor se reproduce en recipientes con agua estancada cerca de las viviendas
              </p>
            </div>

            <div className="flex flex-col items-center text-center group p-4 sm:p-0 sm:col-span-2 md:col-span-1">
              <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2 sm:mb-3">Prevención</h3>
              <p className="text-base leading-relaxed text-gray-700">
                La eliminación temprana de criaderos es la forma más efectiva de control del dengue
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Por Qué Sentrix */}
      <section className="bg-stone-50 py-12 sm:py-16 md:py-24">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8 sm:mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-800 mb-4 sm:mb-6">
              Por Qué Sentrix
            </h2>
          </div>

          <div className="max-w-4xl mx-auto">
            <p className="text-base leading-relaxed text-gray-700 text-justify px-2">
              Sentrix nace como respuesta a una problemática más amplia que la del mosquito Aedes aegypti. Surge de la necesidad de vigilar y comprender el entorno urbano en su conjunto: los criaderos del vector son solo una manifestación visible de fallas más profundas como la acumulación de basura, el agua estancada, el mal mantenimiento de calles y espacios públicos.
            </p>
            <p className="text-base leading-relaxed text-gray-700 text-justify mt-3 sm:mt-4 px-2">
              El nombre combina sentinel (vigía) con el sufijo tecnológico "-x", expresando una vigilancia extendida e inteligente, potenciada por análisis automatizado. Sentrix representa una mirada tecnológica sobre un desafío ambiental y sanitario, integrando visión por computadora, inteligencia artificial y geolocalización para convertir la observación en acción preventiva.
            </p>
            <p className="text-base leading-relaxed text-gray-700 text-justify mt-3 sm:mt-4 px-2">
              Más que una herramienta de detección, Sentrix es una propuesta de gestión inteligente del riesgo urbano, capaz de aportar información útil para la toma de decisiones públicas y comunitarias. Su esencia es la prevención proactiva: anticipar los brotes antes de que ocurran, y promover ciudades más limpias, seguras y resilientes.
            </p>
          </div>
        </div>
      </section>

      {/* Stats Section - Layout Asimétrico */}
      <section className="bg-white py-12 sm:py-16 md:py-24">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          {/* Título existente - mantener igual */}
          <div className="text-center mb-8 sm:mb-12 md:mb-16">
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-800 mb-3 sm:mb-4">
              Resultados del Sistema
            </h2>
            <p className="text-base leading-relaxed text-gray-700 max-w-2xl mx-auto px-2">
              Métricas de rendimiento y detecciones procesadas hasta la fecha
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
      </section>

      {/* Niveles de Riesgo */}
      <section className="bg-stone-50 py-12 sm:py-16 md:py-24">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8 sm:mb-12 md:mb-16">
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-800 mb-3 sm:mb-4">
              Niveles de Riesgo
            </h2>
            <p className="text-base leading-relaxed text-gray-700 max-w-2xl mx-auto px-2">
              Clasificación automática basada en densidad de criaderos detectados y factores ambientales
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
            {/* Bajo */}
            <div className="group text-center p-6 rounded-xl bg-gradient-to-br from-green-100 to-emerald-100 border border-green-200 hover:border-green-300 hover:shadow-sm hover:-translate-y-1 transition-all duration-500">
              <h5 className="text-xl font-bold text-green-600 mb-2 group-hover:scale-105 transition-transform duration-300">Bajo</h5>
              <p className="text-sm text-green-600 mb-4">0-25%</p>
              <p className="text-sm text-gray-600 mb-4">
                Zona con baja concentración de criaderos. Monitoreo preventivo recomendado.
              </p>
              <p className="text-sm text-green-600 font-medium">
                Riesgo controlado
              </p>
            </div>

            {/* Medio */}
            <div className="group text-center p-6 rounded-xl bg-gradient-to-br from-yellow-100 to-amber-100 border border-yellow-200 hover:border-yellow-300 hover:shadow-sm hover:-translate-y-1 transition-all duration-500">
              <h5 className="text-xl font-bold text-yellow-600 mb-2 group-hover:scale-105 transition-transform duration-300">Medio</h5>
              <p className="text-sm text-yellow-600 mb-4">25-50%</p>
              <p className="text-sm text-gray-600 mb-4">
                Concentración moderada. Requiere vigilancia activa y medidas preventivas.
              </p>
              <p className="text-sm text-yellow-600 font-medium">
                Vigilancia requerida
              </p>
            </div>

            {/* Alto */}
            <div className="group text-center p-6 rounded-xl bg-gradient-to-br from-orange-100 to-red-100 border border-orange-200 hover:border-orange-300 hover:shadow-sm hover:-translate-y-1 transition-all duration-500">
              <h5 className="text-xl font-bold text-orange-600 mb-2 group-hover:scale-105 transition-transform duration-300">Alto</h5>
              <p className="text-sm text-orange-600 mb-4">50-75%</p>
              <p className="text-sm text-gray-600 mb-4">
                Alta densidad de criaderos. Intervención inmediata necesaria.
              </p>
              <p className="text-sm text-orange-600 font-medium">
                Acción inmediata
              </p>
            </div>

            {/* Crítico */}
            <div className="group text-center p-6 rounded-xl bg-gradient-to-br from-red-100 to-pink-100 border border-red-200 hover:border-red-300 hover:shadow-sm hover:-translate-y-1 transition-all duration-500">
              <h5 className="text-xl font-bold text-red-600 mb-2 group-hover:scale-105 transition-transform duration-300">Crítico</h5>
              <p className="text-sm text-red-600 mb-4">75-100%</p>
              <p className="text-sm text-gray-600 mb-4">
                Concentración extrema. Alerta sanitaria y control de emergencia.
              </p>
              <p className="text-sm text-red-600 font-medium">
                Emergencia sanitaria
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Mapa de Detecciones */}
      <section className="bg-white py-12 sm:py-16 md:py-24">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8 sm:mb-12 md:mb-16">
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-800 mb-3 sm:mb-4">
              Mapa de Detecciones en Tiempo Real
            </h2>
            <p className="text-base leading-relaxed text-gray-700 max-w-2xl mx-auto px-2">
              Visualiza las áreas monitoreadas y los focos de riesgo detectados por el sistema de IA
              en la provincia de Tucumán
            </p>
          </div>

          <div className="group bg-white rounded-xl p-6 border border-gray-200 hover:border-primary-200 hover:shadow-sm transition-all duration-500">
            {isLoading ? (
              <div className="relative h-64 sm:h-80 md:h-96 bg-stone-50 rounded-xl border-2 border-dashed border-gray-300 flex items-center justify-center">
                <div className="text-center px-4">
                  <div className="relative mb-4 sm:mb-6">
                    <div className="animate-spin h-12 w-12 sm:h-16 sm:w-16 border-4 border-stone-200 border-t-primary-600 rounded-full mx-auto"></div>
                  </div>
                  <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2 sm:mb-3">Cargando Mapa de Calor</h3>
                  <p className="text-base leading-relaxed text-gray-700">
                    Procesando datos de <span className="font-medium text-primary-600">{mapStats?.active_zones || 0}</span> ubicaciones...
                  </p>
                </div>
              </div>
            ) : (
              <>
                {console.log('Rendering HeatMap with data:', heatMapData)}
                <HeatMap
                  data={heatMapData}
                  center={[-26.8083, -65.2176]}
                  zoom={13}
                  className="h-64 sm:h-80 md:h-96 w-full rounded-xl overflow-hidden"
                />
              </>
            )}
          </div>
        </div>
      </section>
    </div>
  )
}

export default HomePage