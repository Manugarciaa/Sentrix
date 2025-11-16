import React, { useState, useEffect, lazy, Suspense } from 'react'
import { MapPin } from 'lucide-react'
import HeroSection from '@/components/public/HeroSection'
import InfoSection from '@/components/public/InfoSection'
import AboutSentrix from '@/components/public/AboutSentrix'
import { config, apiEndpoints } from '@/lib/config'

// Lazy load heavy components
const HeatMap = lazy(() => import('@/components/map/HeatMap'))
const AboutDengue = lazy(() => import('@/components/public/AboutDengue'))
const DemoSection = lazy(() => import('@/components/public/DemoSection'))

interface MapStats {
  total_analyses: number
  total_detections: number
  locations_with_gps: number
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

  // Fetch real data from backend - with requestIdleCallback for better performance
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

    // Use requestIdleCallback to avoid blocking main thread
    if ('requestIdleCallback' in window) {
      requestIdleCallback(() => fetchData(), { timeout: 2000 })
    } else {
      // Fallback for browsers that don't support requestIdleCallback
      setTimeout(fetchData, 100)
    }
  }, [])

  return (
    <div className="flex flex-col bg-background">
      {/* 1. Hero Section */}
      <HeroSection />

      {/* 2. About Sentrix - El proyecto */}
      <AboutSentrix />

      {/* 3. Info Section */}
      <InfoSection />

      {/* 4. About Dengue - Información educativa */}
      <Suspense fallback={<div className="min-h-[400px] bg-background" />}>
        <AboutDengue />
      </Suspense>

      {/* 5. Demo Section - Prueba de IA */}
      <Suspense fallback={<div className="min-h-screen bg-background" />}>
        <DemoSection />
      </Suspense>

      {/* 6. Niveles de Riesgo - Educación */}
      <section className="bg-background py-16 sm:py-20 md:py-24">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-foreground mb-4">
              Entendé los niveles de riesgo
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Clasificación automática basada en densidad de criaderos y factores ambientales
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Bajo */}
            <div className="group text-center p-4 sm:p-6 rounded-2xl bg-status-success-light border-2 border-status-success-border hover:border-status-success hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
              <h5 className="text-2xl font-bold text-status-success-text mb-2">Bajo</h5>
              <p className="text-sm text-status-success-muted mb-4 font-semibold">0-25%</p>
              <p className="text-sm text-foreground/80 leading-relaxed">
                Zona con baja concentración de criaderos. Monitoreo preventivo recomendado.
              </p>
            </div>

            {/* Medio */}
            <div className="group text-center p-4 sm:p-6 rounded-2xl bg-status-warning-light border-2 border-status-warning-border hover:border-status-warning hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
              <h5 className="text-2xl font-bold text-status-warning-text mb-2">Medio</h5>
              <p className="text-sm text-status-warning-muted mb-4 font-semibold">25-50%</p>
              <p className="text-sm text-foreground/80 leading-relaxed">
                Concentración moderada. Requiere vigilancia activa y medidas preventivas.
              </p>
            </div>

            {/* Alto */}
            <div className="group text-center p-4 sm:p-6 rounded-2xl bg-status-danger-light border-2 border-status-danger-border hover:border-status-danger hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
              <h5 className="text-2xl font-bold text-status-danger-text mb-2">Alto</h5>
              <p className="text-sm text-status-danger-muted mb-4 font-semibold">50-75%</p>
              <p className="text-sm text-foreground/80 leading-relaxed">
                Alta densidad de criaderos. Intervención inmediata necesaria.
              </p>
            </div>

            {/* Crítico */}
            <div className="group text-center p-4 sm:p-6 rounded-2xl bg-status-critical-light border-2 border-status-critical-border hover:border-status-critical hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
              <h5 className="text-2xl font-bold text-status-critical-text mb-2">Crítico</h5>
              <p className="text-sm text-status-critical-muted mb-4 font-semibold">75-100%</p>
              <p className="text-sm text-foreground/80 leading-relaxed">
                Densidad muy elevada. Requiere atención prioritaria de las autoridades sanitarias.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 7. Mapa de Zonas Afectadas */}
      <section className="bg-background min-h-screen flex items-center py-16 sm:py-20">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 w-full">
          <div className="text-center mb-12">
            <h2 id="mapa" className="scroll-mt-24 text-3xl sm:text-4xl font-bold text-foreground mb-4">
              Zonas afectadas en Tucumán
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Visualiza las áreas monitoreadas y los focos de riesgo detectados en tiempo real
            </p>
          </div>

          <div className="group bg-card rounded-2xl p-6 border border-border hover:border-primary/30 dark:hover:border-primary/50 hover:shadow-lg transition-all duration-500">
            <div className="relative h-96 md:h-[500px] z-0">
              <Suspense fallback={<div className="h-full w-full rounded-xl overflow-hidden bg-muted/20 flex items-center justify-center"><p className="text-muted-foreground">Cargando mapa...</p></div>}>
                <HeatMap
                  data={heatMapData}
                  center={[-26.8083, -65.2176]}
                  zoom={13}
                  className="h-full w-full rounded-xl overflow-hidden"
                  visualizationMode="risk-level"
                />
              </Suspense>
              {heatMapData.length === 0 && (
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-[5]">
                  <div className="bg-card/70 backdrop-blur-sm rounded-2xl p-6 sm:p-8 shadow-xl border border-primary/15 max-w-md mx-4 transition-all duration-300">
                    <div className="rounded-full p-4 w-20 h-20 mx-auto mb-5 flex items-center justify-center bg-primary/8">
                      <MapPin className="h-10 w-10 text-primary/70" />
                    </div>
                    <h3 className="text-xl font-bold text-foreground/90 mb-3 text-center">
                      Sin datos disponibles
                    </h3>
                    <p className="text-sm text-muted-foreground/80 text-center leading-relaxed">
                      Aún no hay detecciones registradas. Las ubicaciones aparecerán aquí
                      cuando se procesen reportes de la comunidad.
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
