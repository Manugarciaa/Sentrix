import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { routes, config, apiEndpoints } from '@/lib/config'
import { ArrowRight, CheckCircle, MapPin } from 'lucide-react'
import HeatMap from '@/components/map/HeatMap'

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

interface HeatMapDataPoint {
  latitude: number
  longitude: number
  intensity: number
  riskLevel: 'ALTO' | 'MEDIO' | 'BAJO'
  detectionCount: number
  breedingSiteType?: string | null
  timestamp?: string
}

const HomePage: React.FC = () => {
  const [heatMapData, setHeatMapData] = useState<HeatMapDataPoint[]>([])
  const [mapStats, setMapStats] = useState<MapStats | null>(null)

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
          // Only set data if it exists, otherwise keep empty array
          setHeatMapData(heatmapResponse_data.data || [])
        }

        if (statsResponse.ok) {
          const statsData = await statsResponse.json()
          setMapStats(statsData)
        }
      } catch (error) {
        console.error('Error fetching map data:', error)
        // Keep empty array on error
        setHeatMapData([])
      }
    }

    fetchData()
  }, [])

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
                Casos de dengue a nivel mundial cada año, con un crecimiento constante
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

      {/* Niveles de Riesgo */}
      <section className="bg-white py-12 sm:py-16 md:py-24">
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
      <section className="bg-stone-50 py-12 sm:py-16 md:py-24">
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
            <div className="relative h-64 sm:h-80 md:h-96">
              <HeatMap
                data={heatMapData}
                center={[-26.8083, -65.2176]}
                zoom={13}
                className="h-full w-full rounded-xl overflow-hidden"
                visualizationMode="risk-level"
              />
              {heatMapData.length === 0 && (
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <div className="bg-white/95 backdrop-blur-sm rounded-xl p-6 shadow-lg border border-gray-200 max-w-md mx-4">
                    <MapPin className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2 text-center">
                      Sin Datos Disponibles
                    </h3>
                    <p className="text-sm text-gray-600 text-center">
                      Aún no hay detecciones registradas en el sistema. Las ubicaciones aparecerán aquí una vez que se procesen imágenes.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

export default HomePage
