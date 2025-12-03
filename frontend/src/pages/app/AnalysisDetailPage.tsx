import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft, Download, FileText, MapPin, Calendar,
  Image as ImageIcon, Cpu, AlertCircle, Maximize2, X,
  ZoomIn, ZoomOut, Info
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/Tabs'
import { SkeletonAnalysisDetail } from '@/components/ui/custom-skeletons'
import { DetectionCard } from '@/components/domain/DetectionCard'
import { ValidationModal } from '@/components/domain/ValidationModal'
import { RiskBadge } from '@/components/domain/RiskBadge'
import HeatMap from '@/components/map/HeatMap'
import { apiEndpoints, env } from '@/lib/config'
import { useAuthStore } from '@/store/auth'
import { apiClient } from '@/api/client'
import type { Analysis, Detection } from '@/types'

// Helper function to normalize image URLs
const normalizeImageUrl = (url: string | undefined): string | undefined => {
  if (!url) return undefined

  // Si ya es una URL completa (http/https), devolverla tal cual
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }

  // Verificar que supabaseUrl esté configurado
  if (!env.supabaseUrl) {
    console.error('VITE_SUPABASE_URL no está configurado en .env')
    return undefined
  }

  // Si es una ruta relativa temporal (temp/...), construir URL de Supabase Storage
  if (url.startsWith('temp/')) {
    const filename = url.replace('temp/', '')
    return `${env.supabaseUrl}/storage/v1/object/public/sentrix-images/${filename}`
  }

  // Si comienza con "original_", usar bucket sentrix-images
  if (url.startsWith('original_')) {
    return `${env.supabaseUrl}/storage/v1/object/public/sentrix-images/${url}`
  }

  // Si comienza con "processed_", usar bucket sentrix-processed
  if (url.startsWith('processed_')) {
    return `${env.supabaseUrl}/storage/v1/object/public/sentrix-processed/${url}`
  }

  // Si es un UUID (archivo de Supabase sin prefijo), asumir bucket sentrix-images
  if (url.match(/^[0-9a-f-]+\.(jpg|jpeg|png|webp|tiff)$/i)) {
    return `${env.supabaseUrl}/storage/v1/object/public/sentrix-images/${url}`
  }

  // Si es un nombre de archivo SENTRIX_..., asumir bucket sentrix-images
  if (url.startsWith('SENTRIX_')) {
    return `${env.supabaseUrl}/storage/v1/object/public/sentrix-images/${url}`
  }

  // Por defecto, asumir que es del bucket sentrix-images
  return `${env.supabaseUrl}/storage/v1/object/public/sentrix-images/${url}`
}

const AnalysisDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuthStore()

  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedDetection, setSelectedDetection] = useState<Detection | null>(null)
  const [validationModalOpen, setValidationModalOpen] = useState(false)
  const [isValidating, setIsValidating] = useState(false)
  const [isImageModalOpen, setIsImageModalOpen] = useState(false)
  const [modalImageType, setModalImageType] = useState<'original' | 'processed'>('processed')
  const [zoomLevel, setZoomLevel] = useState(1)

  const canValidate = user?.role === 'ADMIN' || user?.role === 'EXPERT'

  useEffect(() => {
    if (id) {
      fetchAnalysisDetail()
    }
  }, [id])

  const fetchAnalysisDetail = async (retryCount = 0) => {
    const MAX_RETRIES = 5
    const RETRY_DELAY = 2500

    try {
      if (retryCount === 0) {
        setIsLoading(true)
        setError(null)
      }

      const data = await apiClient.get(apiEndpoints.analyses.detail(id!))

      setAnalysis(data)
      setIsLoading(false)
      setError(null)
    } catch (err: any) {
      const isNotFound = err.message?.includes('404') || err.message?.includes('not found')

      if (isNotFound && retryCount < MAX_RETRIES) {
        if (import.meta.env.DEV && retryCount === 0) {
          console.log(`Esperando a que el análisis esté disponible... (intento ${retryCount + 1}/${MAX_RETRIES + 1})`)
        }

        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY))
        return fetchAnalysisDetail(retryCount + 1)
      }

      console.error('Error fetching analysis:', err)
      setError(
        isNotFound
          ? 'El análisis aún se está procesando. Por favor, recarga la página en unos momentos.'
          : 'Error al cargar el análisis.'
      )
      setIsLoading(false)
    }
  }

  const handleValidateDetection = async (
    detectionId: string,
    status: 'validated_positive' | 'validated_negative',
    notes?: string
  ) => {
    try {
      setIsValidating(true)

      await apiClient.post(
        `/api/detections/${detectionId}/validate`,
        {
          validation_status: status,
          validation_notes: notes,
        }
      )

      await fetchAnalysisDetail()
    } catch (err) {
      console.error('Validation error:', err)
      throw err
    } finally {
      setIsValidating(false)
    }
  }

  const handleDetectionClick = (detection: Detection) => {
    setSelectedDetection(detection)
    if (canValidate && detection.validation_status === 'pending_validation') {
      setValidationModalOpen(true)
    }
  }

  const handleExportPDF = () => {
    console.log('Exporting to PDF...')
  }

  const handleExportJSON = () => {
    if (!analysis) return

    const dataStr = JSON.stringify(analysis, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr)
    const exportFileDefaultName = `analysis-${analysis.id}.json`

    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()
  }

  const openImageModal = (type: 'original' | 'processed') => {
    setModalImageType(type)
    setZoomLevel(1)
    setIsImageModalOpen(true)
  }

  const closeImageModal = () => {
    setIsImageModalOpen(false)
    setZoomLevel(1)
  }

  const handleZoomIn = () => {
    setZoomLevel(prev => Math.min(prev + 0.25, 3))
  }

  const handleZoomOut = () => {
    setZoomLevel(prev => Math.max(prev - 0.25, 0.5))
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'N/A'
    return (bytes / 1024 / 1024).toFixed(2) + ' MB'
  }

  if (isLoading) {
    return <SkeletonAnalysisDetail />
  }

  if (error || !analysis) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-foreground mb-2">Error</h3>
          <p className="text-sm text-muted-foreground mb-4">{error || 'No se encontró el análisis'}</p>
          <Button onClick={() => navigate('/app/analysis')}>
            Volver a Análisis
          </Button>
        </div>
      </div>
    )
  }

  // Check if location exists - either from location object or google_maps_url
  const hasLocationCoords = (analysis.location?.latitude && analysis.location?.longitude) ||
                            (analysis.google_maps_url && analysis.google_maps_url.includes('?q='))
  const hasLocation = analysis.location?.has_location ?? analysis.has_gps_data ?? hasLocationCoords
  const detectionCount = analysis.detections?.length || 0
  const pendingValidationCount = analysis.detections?.filter(
    d => d.validation_status === 'pending_validation'
  ).length || 0

  return (
    <div className="space-y-4 sm:space-y-6 pb-8">
      {/* Header - Responsive */}
      <div className="flex flex-col gap-3 sm:gap-4">
        <div className="flex items-center gap-2 sm:gap-3">
          <Button
            onClick={() => navigate('/app/analysis')}
            variant="outline"
            size="sm"
            className="flex-shrink-0"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver
          </Button>
        </div>

        <div className="flex flex-col gap-3 sm:gap-4">
          <div className="flex flex-col gap-2">
            <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3">
              <h1 className="text-2xl sm:text-3xl font-bold text-foreground">
                Análisis #{analysis.id.slice(0, 8)}
              </h1>
              <RiskBadge level={analysis.risk_assessment?.level || 'BAJO'} />
            </div>
            <div className="flex flex-col sm:flex-row sm:flex-wrap sm:items-center gap-2 sm:gap-3 text-xs sm:text-sm text-muted-foreground">
              <div className="flex items-center gap-1.5">
                <Calendar className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
                <span className="truncate">{formatDate(analysis.created_at)}</span>
              </div>
              {analysis.image_filename && (
                <>
                  <span className="hidden sm:inline">•</span>
                  <div className="flex items-center gap-1.5 min-w-0">
                    <ImageIcon className="h-3.5 w-3.5 sm:h-4 sm:w-4 flex-shrink-0" />
                    <span className="truncate">{analysis.image_filename}</span>
                  </div>
                </>
              )}
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
            <Button
              onClick={handleExportJSON}
              variant="outline"
              size="sm"
              className="w-full sm:w-auto justify-center"
            >
              <Download className="h-4 w-4 mr-2" />
              JSON
            </Button>
            <Button
              onClick={handleExportPDF}
              variant="outline"
              size="sm"
              className="w-full sm:w-auto justify-center"
            >
              <FileText className="h-4 w-4 mr-2" />
              PDF
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="space-y-4">
        {/* Images and Map Grid - Responsive */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Images - Takes 2 columns on large screens */}
          <Card className="lg:col-span-2 order-1 lg:order-1">
            <div className="p-3 border-b bg-gradient-to-r from-primary/5 to-transparent">
              <h2 className="text-base font-semibold">Análisis Visual</h2>
            </div>

            <Tabs defaultValue="processed" className="w-full">
              <div className="px-3 pt-3">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="processed" className="gap-1.5 text-xs">
                    <ImageIcon className="h-3 w-3" />
                    Con Detecciones
                  </TabsTrigger>
                  <TabsTrigger value="original" className="gap-1.5 text-xs">
                    <ImageIcon className="h-3 w-3" />
                    Original
                  </TabsTrigger>
                </TabsList>
              </div>

              <TabsContent value="processed" className="p-3 m-0">
                {normalizeImageUrl(analysis.processed_image_url || analysis.image_url) ? (
                  <div className="space-y-2">
                    {/* Image Container - More Compact */}
                    <div className="relative group bg-gradient-to-br from-muted/20 to-muted/10 rounded-lg p-2 border border-muted/50 hover:border-primary/30 transition-all">
                      <div className="relative overflow-hidden rounded-md bg-black/5">
                        <img
                          src={normalizeImageUrl(analysis.processed_image_url || analysis.image_url)}
                          alt="Imagen procesada"
                          className="w-full h-auto max-h-[400px] object-contain cursor-pointer transition-all group-hover:scale-[1.01]"
                          onClick={() => openImageModal('processed')}
                        />
                      </div>
                      <button
                        onClick={() => openImageModal('processed')}
                        className="absolute top-4 right-4 bg-black/70 hover:bg-black/90 text-white p-2 rounded-md shadow-lg opacity-0 group-hover:opacity-100 transition-all backdrop-blur-sm"
                      >
                        <Maximize2 className="h-4 w-4" />
                      </button>
                    </div>

                    {/* Legend - Responsive */}
                    {detectionCount > 0 && (
                      <div className="bg-gradient-to-br from-card to-muted/10 border border-primary/10 rounded-lg p-2 sm:p-2.5">
                        <div className="flex items-center gap-1.5 mb-1.5 sm:mb-2">
                          <Info className="h-3 w-3 sm:h-3.5 sm:w-3.5 text-primary" />
                          <h3 className="text-[10px] sm:text-xs font-semibold">Tipos de Criadero</h3>
                        </div>
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-1.5 sm:gap-2">
                          <div className="flex items-center gap-1 sm:gap-1.5 p-1 sm:p-1.5 rounded-md bg-background/80 border border-muted">
                            <div className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full bg-[rgb(255,140,0)] shadow-sm flex-shrink-0" />
                            <span className="text-[10px] sm:text-xs font-medium truncate">Basura</span>
                          </div>
                          <div className="flex items-center gap-1 sm:gap-1.5 p-1 sm:p-1.5 rounded-md bg-background/80 border border-muted">
                            <div className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full bg-[rgb(0,100,255)] shadow-sm flex-shrink-0" />
                            <span className="text-[10px] sm:text-xs font-medium truncate">Agua</span>
                          </div>
                          <div className="flex items-center gap-1 sm:gap-1.5 p-1 sm:p-1.5 rounded-md bg-background/80 border border-muted">
                            <div className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full bg-[rgb(0,200,0)] shadow-sm flex-shrink-0" />
                            <span className="text-[10px] sm:text-xs font-medium truncate">Huecos</span>
                          </div>
                          <div className="flex items-center gap-1 sm:gap-1.5 p-1 sm:p-1.5 rounded-md bg-background/80 border border-muted">
                            <div className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full bg-[rgb(255,0,0)] shadow-sm flex-shrink-0" />
                            <span className="text-[10px] sm:text-xs font-medium truncate">Calles</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center h-48 bg-muted/30 rounded-lg border-2 border-dashed border-muted">
                    <ImageIcon className="h-10 w-10 text-muted-foreground/50 mb-2" />
                    <p className="text-sm text-muted-foreground font-medium">No disponible</p>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="original" className="p-3 m-0">
                {normalizeImageUrl(analysis.image_url) ? (
                  <div className="space-y-2">
                    {/* Image Container - More Compact */}
                    <div className="relative group bg-gradient-to-br from-muted/20 to-muted/10 rounded-lg p-2 border border-muted/50 hover:border-primary/30 transition-all">
                      <div className="relative overflow-hidden rounded-md bg-black/5">
                        <img
                          src={normalizeImageUrl(analysis.image_url)}
                          alt="Imagen original"
                          className="w-full h-auto max-h-[400px] object-contain cursor-pointer transition-all group-hover:scale-[1.01]"
                          onClick={() => openImageModal('original')}
                        />
                      </div>
                      <button
                        onClick={() => openImageModal('original')}
                        className="absolute top-4 right-4 bg-black/70 hover:bg-black/90 text-white p-2 rounded-md shadow-lg opacity-0 group-hover:opacity-100 transition-all backdrop-blur-sm"
                      >
                        <Maximize2 className="h-4 w-4" />
                      </button>
                    </div>

                    {/* Image Info - Compact */}
                    <div className="bg-gradient-to-br from-card to-muted/10 border border-muted rounded-lg p-2.5">
                      <div className="flex items-center gap-1.5 mb-1.5">
                        <ImageIcon className="h-3.5 w-3.5 text-primary" />
                        <h3 className="text-xs font-semibold">Información</h3>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div>
                          <span className="text-muted-foreground">Archivo</span>
                          <p className="font-medium truncate text-xs mt-0.5">
                            {analysis.image_filename || 'N/A'}
                          </p>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Tamaño</span>
                          <p className="font-medium mt-0.5">{formatFileSize(analysis.image_size_bytes)}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center h-48 bg-muted/30 rounded-lg border-2 border-dashed border-muted">
                    <ImageIcon className="h-10 w-10 text-muted-foreground/50 mb-2" />
                    <p className="text-sm text-muted-foreground font-medium">No disponible</p>
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </Card>

          {/* Detalles del Análisis - Takes 1 column on large screens */}
          <Card className="lg:col-span-1 order-2 lg:order-2">
            <div className="p-3 border-b">
              <h2 className="text-base font-semibold">Detalles del Análisis</h2>
            </div>
            <div className="p-3 space-y-3">
              {/* Statistics Section */}
              <div className="pb-3 border-b">
                <div className="flex items-center gap-1.5 mb-2">
                  <Info className="h-3.5 w-3.5 text-primary" />
                  <h3 className="text-xs font-semibold">Estadísticas</h3>
                </div>
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs">
                    <span className="text-muted-foreground">Detecciones</span>
                    <span className="font-medium">{detectionCount}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-muted-foreground">Pendientes</span>
                    <span className="font-medium text-amber-600">{pendingValidationCount}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-muted-foreground">Confianza</span>
                    <span className="font-medium">
                      {analysis.detections?.length > 0
                        ? Math.round(
                            analysis.detections.reduce((sum, d) => sum + d.confidence, 0) /
                            analysis.detections.length * 100
                          )
                        : 0}%
                    </span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-muted-foreground">Tiempo</span>
                    <span className="font-medium">
                      {analysis.processing_time_ms
                        ? `${(analysis.processing_time_ms / 1000).toFixed(1)}s`
                        : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-muted-foreground">Tamaño</span>
                    <span className="font-medium">{formatFileSize(analysis.image_size_bytes)}</span>
                  </div>
                </div>
              </div>

              {/* Location Section with Map - Only if has location */}
              {hasLocation && (() => {
                let lat: number | undefined
                let lng: number | undefined
                let source = 'DESCONOCIDO'

                if (analysis.location?.latitude && analysis.location?.longitude) {
                  lat = analysis.location.latitude
                  lng = analysis.location.longitude
                  source = analysis.location.location_source || 'GPS'
                } else if (analysis.google_maps_url) {
                  const match = analysis.google_maps_url.match(/\?q=([\d.-]+),([\d.-]+)/)
                  if (match) {
                    lat = parseFloat(match[1])
                    lng = parseFloat(match[2])
                    source = 'MANUAL'
                  }
                }

                if (!lat || !lng) return null

                return (
                  <div className="pb-3 border-b">
                    <div className="flex items-center gap-1.5 mb-2">
                      <MapPin className="h-3.5 w-3.5 text-primary" />
                      <h3 className="text-xs font-semibold">Ubicación</h3>
                    </div>
                    <div className="space-y-2 mb-2">
                      <div className="flex justify-between text-xs">
                        <span className="text-muted-foreground">Coordenadas</span>
                        <span className="font-mono text-xs font-medium text-right">
                          {lat.toFixed(7)}, {lng.toFixed(7)}
                        </span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-muted-foreground">Fuente</span>
                        <span className="font-medium">{source}</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-muted-foreground">Precisión</span>
                        <span className="font-medium text-xs text-muted-foreground">~5-50m</span>
                      </div>
                      {analysis.google_maps_url && (
                        <a
                          href={analysis.google_maps_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-primary hover:underline flex items-center gap-1"
                        >
                          <MapPin className="h-3 w-3" />
                          Ver en Google Maps
                        </a>
                      )}
                    </div>
                    {/* Small Map */}
                    <div className="rounded-lg overflow-hidden border border-muted">
                      <HeatMap
                        data={[{
                          latitude: lat,
                          longitude: lng,
                          intensity: 1,
                          riskLevel: analysis.risk_assessment?.level || 'BAJO',
                          detectionCount: detectionCount,
                        }]}
                        center={[lat, lng]}
                        zoom={17}
                        className="h-48 w-full"
                      />
                    </div>
                  </div>
                )
              })()}

              {/* Analysis Info Section */}
              <div className="pb-3 border-b">
                <div className="flex items-center gap-1.5 mb-2">
                  <Cpu className="h-3.5 w-3.5 text-primary" />
                  <h3 className="text-xs font-semibold">Información Técnica</h3>
                </div>
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs">
                    <span className="text-muted-foreground">Modelo IA</span>
                    <span className="font-medium text-right">{analysis.model_used || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-muted-foreground">Umbral</span>
                    <span className="font-medium">
                      {analysis.confidence_threshold
                        ? `${(analysis.confidence_threshold * 100).toFixed(0)}%`
                        : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-muted-foreground">Versión</span>
                    <span className="font-medium">{analysis.yolo_service_version || 'N/A'}</span>
                  </div>
                </div>
              </div>

              {/* Camera Info Section - Only if exists */}
              {analysis.camera_info && (analysis.camera_info.camera_make || analysis.camera_info.camera_model) && (
                <div>
                  <div className="flex items-center gap-1.5 mb-2">
                    <ImageIcon className="h-3.5 w-3.5 text-primary" />
                    <h3 className="text-xs font-semibold">Dispositivo de Captura</h3>
                  </div>
                  <div className="space-y-1.5">
                    {analysis.camera_info.camera_make && (
                      <div className="flex justify-between text-xs">
                        <span className="text-muted-foreground">Marca</span>
                        <span className="font-medium">{analysis.camera_info.camera_make}</span>
                      </div>
                    )}
                    {analysis.camera_info.camera_model && (
                      <div className="flex justify-between text-xs">
                        <span className="text-muted-foreground">Modelo</span>
                        <span className="font-medium">{analysis.camera_info.camera_model}</span>
                      </div>
                    )}
                    {analysis.camera_info.camera_software && (
                      <div className="flex justify-between text-xs">
                        <span className="text-muted-foreground">Software</span>
                        <span className="font-medium text-right text-xs">
                          {analysis.camera_info.camera_software}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* Detections - Full Width */}
        <Card>
          <div className="p-3 border-b">
            <h2 className="text-base font-semibold">Detecciones ({detectionCount})</h2>
          </div>

          {/* Mostrar tabs solo para ADMIN/EXPERT */}
          {canValidate ? (
            <Tabs defaultValue="all" className="w-full">
              <div className="px-3 pt-3">
                <TabsList className="text-xs">
                  <TabsTrigger value="all" className="text-xs">Todas ({detectionCount})</TabsTrigger>
                  <TabsTrigger value="pending" className="text-xs">Pendientes ({pendingValidationCount})</TabsTrigger>
                  <TabsTrigger value="validated" className="text-xs">Validadas ({detectionCount - pendingValidationCount})</TabsTrigger>
                </TabsList>
              </div>

              <TabsContent value="all" className="p-3">
                {detectionCount > 0 ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {analysis.detections.map((detection) => (
                      <DetectionCard
                        key={detection.id}
                        detection={detection}
                        onValidate={handleValidateDetection}
                        showActions={true}
                      />
                    ))}
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-24 text-sm text-muted-foreground">
                    No hay detecciones
                  </div>
                )}
              </TabsContent>

              <TabsContent value="pending" className="p-3">
                {pendingValidationCount > 0 ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {analysis.detections
                      .filter(d => d.validation_status === 'pending_validation')
                      .map((detection) => (
                        <DetectionCard
                          key={detection.id}
                          detection={detection}
                          onValidate={handleValidateDetection}
                          showActions={true}
                        />
                      ))}
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-24 text-sm text-muted-foreground">
                    No hay detecciones pendientes
                  </div>
                )}
              </TabsContent>

              <TabsContent value="validated" className="p-3">
                {detectionCount - pendingValidationCount > 0 ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {analysis.detections
                      .filter(d =>
                        d.validation_status === 'validated_positive' ||
                        d.validation_status === 'validated_negative'
                      )
                      .map((detection) => (
                        <DetectionCard
                          key={detection.id}
                          detection={detection}
                          showActions={false}
                        />
                      ))}
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-24 text-sm text-muted-foreground">
                    No hay detecciones validadas
                  </div>
                )}
              </TabsContent>
            </Tabs>
          ) : (
            /* Vista simple para usuarios regulares - sin tabs */
            <div className="p-3">
              {detectionCount > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {analysis.detections.map((detection) => (
                    <DetectionCard
                      key={detection.id}
                      detection={detection}
                      showActions={false}
                    />
                  ))}
                </div>
              ) : (
                <div className="flex items-center justify-center h-24 text-sm text-muted-foreground">
                  No hay detecciones
                </div>
              )}
            </div>
          )}
        </Card>
      </div>

      {/* Image Modal */}
      {isImageModalOpen && (
        <div
          className="fixed inset-0 z-50 bg-black/95 flex items-center justify-center p-4"
          onClick={closeImageModal}
        >
          <button
            onClick={closeImageModal}
            className="absolute top-2 right-2 sm:top-4 sm:right-4 z-10 bg-white/10 hover:bg-white/20 backdrop-blur-sm rounded-full p-2 sm:p-2.5 transition-colors"
          >
            <X className="h-5 w-5 sm:h-6 sm:w-6 text-white" />
          </button>

          <div className="absolute top-2 left-2 sm:top-4 sm:left-4 z-10 flex gap-1.5 sm:gap-2">
            <button
              onClick={(e) => { e.stopPropagation(); handleZoomOut(); }}
              className="bg-white/10 hover:bg-white/20 backdrop-blur-sm rounded-lg px-2 py-1.5 sm:px-3 sm:py-2 transition-colors"
            >
              <ZoomOut className="h-4 w-4 sm:h-5 sm:w-5 text-white" />
            </button>
            <div className="bg-white/10 backdrop-blur-sm rounded-lg px-2 py-1.5 sm:px-4 sm:py-2">
              <span className="text-xs sm:text-sm text-white font-semibold">{Math.round(zoomLevel * 100)}%</span>
            </div>
            <button
              onClick={(e) => { e.stopPropagation(); handleZoomIn(); }}
              className="bg-white/10 hover:bg-white/20 backdrop-blur-sm rounded-lg px-2 py-1.5 sm:px-3 sm:py-2 transition-colors"
            >
              <ZoomIn className="h-4 w-4 sm:h-5 sm:w-5 text-white" />
            </button>
          </div>

          {detectionCount > 0 && modalImageType === 'processed' && (
            <div className="absolute bottom-2 left-2 sm:bottom-4 sm:left-4 z-10 bg-white/10 backdrop-blur-sm rounded-lg px-2 py-1.5 sm:px-4 sm:py-2.5">
              <div className="flex flex-wrap items-center gap-2 sm:gap-4">
                <div className="flex items-center gap-1 sm:gap-1.5">
                  <div className="w-2 h-2 sm:w-3 sm:h-3 rounded-full bg-[rgb(255,140,0)] flex-shrink-0" />
                  <span className="text-[10px] sm:text-xs text-white font-medium">Basura</span>
                </div>
                <div className="flex items-center gap-1 sm:gap-1.5">
                  <div className="w-2 h-2 sm:w-3 sm:h-3 rounded-full bg-[rgb(0,100,255)] flex-shrink-0" />
                  <span className="text-[10px] sm:text-xs text-white font-medium">Agua</span>
                </div>
                <div className="flex items-center gap-1 sm:gap-1.5">
                  <div className="w-2 h-2 sm:w-3 sm:h-3 rounded-full bg-[rgb(0,200,0)] flex-shrink-0" />
                  <span className="text-[10px] sm:text-xs text-white font-medium">Huecos</span>
                </div>
                <div className="flex items-center gap-1 sm:gap-1.5">
                  <div className="w-2 h-2 sm:w-3 sm:h-3 rounded-full bg-[rgb(255,0,0)] flex-shrink-0" />
                  <span className="text-[10px] sm:text-xs text-white font-medium">Calles</span>
                </div>
              </div>
            </div>
          )}

          <div
            className="relative max-w-[90vw] max-h-[90vh] overflow-auto rounded-lg"
            onClick={(e) => e.stopPropagation()}
          >
            <img
              src={
                modalImageType === 'processed'
                  ? normalizeImageUrl(analysis.processed_image_url || analysis.image_url)
                  : normalizeImageUrl(analysis.image_url)
              }
              alt={modalImageType === 'processed' ? 'Imagen procesada' : 'Imagen original'}
              className="w-auto h-auto max-w-none transition-transform duration-200"
              style={{ transform: `scale(${zoomLevel})` }}
            />
          </div>

          <div className="absolute bottom-2 right-2 sm:bottom-4 sm:right-4 z-10 bg-white/10 backdrop-blur-sm rounded-lg px-2 py-1 sm:px-4 sm:py-2">
            <p className="text-[10px] sm:text-xs text-white/90 font-medium">ESC o click fuera para cerrar</p>
          </div>
        </div>
      )}

      {/* Validation Modal */}
      <ValidationModal
        open={validationModalOpen}
        onClose={() => {
          setValidationModalOpen(false)
          setSelectedDetection(null)
        }}
        detection={selectedDetection}
        onValidate={handleValidateDetection}
        isLoading={isValidating}
      />
    </div>
  )
}

export default AnalysisDetailPage
