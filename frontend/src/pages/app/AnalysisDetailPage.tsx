import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft, Download, FileText, MapPin, Calendar, Clock,
  Image as ImageIcon, Cpu, Shield, AlertCircle
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/Tabs'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { ImageViewer } from '@/components/domain/ImageViewer'
import { DetectionCard } from '@/components/domain/DetectionCard'
import { RiskAssessmentCard } from '@/components/domain/RiskAssessmentCard'
import { ValidationModal } from '@/components/domain/ValidationModal'
import { RiskBadge } from '@/components/domain/RiskBadge'
import HeatMap from '@/components/map/HeatMap'
import { config, apiEndpoints } from '@/lib/config'
import { useAuthStore } from '@/store/auth'
import type { Analysis, Detection } from '@/types'

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

  const canValidate = user?.role === 'ADMIN' || user?.role === 'EXPERT'

  useEffect(() => {
    if (id) {
      fetchAnalysisDetail()
    }
  }, [id])

  const fetchAnalysisDetail = async () => {
    try {
      setIsLoading(true)
      setError(null)

      const response = await fetch(
        `${config.api.baseUrl}${apiEndpoints.analyses.detail(id!)}`
      )

      if (response.ok) {
        const data = await response.json()
        setAnalysis(data)
      } else {
        setError('Error al cargar el análisis')
      }
    } catch (err) {
      console.error('Error fetching analysis:', err)
      setError('Error de conexión')
    } finally {
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

      const response = await fetch(
        `${config.api.baseUrl}/api/detections/${detectionId}/validate`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            validation_status: status,
            validation_notes: notes,
          }),
        }
      )

      if (response.ok) {
        // Refresh analysis data
        await fetchAnalysisDetail()
      } else {
        throw new Error('Error al validar la detección')
      }
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
    // TODO: Implement PDF export
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
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-sm text-gray-600">Cargando análisis...</p>
        </div>
      </div>
    )
  }

  if (error || !analysis) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error</h3>
          <p className="text-sm text-gray-600 mb-4">{error || 'No se encontró el análisis'}</p>
          <Button onClick={() => navigate('/app/analysis')}>
            Volver a Análisis
          </Button>
        </div>
      </div>
    )
  }

  const hasLocation = analysis.location?.has_location ?? false
  const detectionCount = analysis.detections?.length || 0
  const pendingValidationCount = analysis.detections?.filter(
    d => d.validation_status === 'pending_validation'
  ).length || 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-4">
          <Button
            onClick={() => navigate('/app/analysis')}
            variant="outline"
            size="sm"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Análisis #{analysis.id.slice(0, 8)}
            </h1>
            <p className="text-sm text-gray-600 mt-1">
              Creado el {formatDate(analysis.created_at)}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Button
            onClick={handleExportJSON}
            variant="outline"
            size="sm"
            className="gap-2"
          >
            <Download className="h-4 w-4" />
            JSON
          </Button>
          <Button
            onClick={handleExportPDF}
            variant="outline"
            size="sm"
            className="gap-2"
          >
            <FileText className="h-4 w-4" />
            PDF
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-100 rounded-lg">
              <Shield className="h-5 w-5 text-red-600" />
            </div>
            <div>
              <p className="text-xs text-gray-600">Detecciones</p>
              <p className="text-2xl font-bold text-gray-900">{detectionCount}</p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-amber-100 rounded-lg">
              <Clock className="h-5 w-5 text-amber-600" />
            </div>
            <div>
              <p className="text-xs text-gray-600">Pendientes</p>
              <p className="text-2xl font-bold text-gray-900">{pendingValidationCount}</p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Cpu className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-xs text-gray-600">Tiempo</p>
              <p className="text-2xl font-bold text-gray-900">
                {analysis.processing_time_ms
                  ? `${(analysis.processing_time_ms / 1000).toFixed(1)}s`
                  : 'N/A'}
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <ImageIcon className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-xs text-gray-600">Tamaño</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatFileSize(analysis.image_size_bytes)}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Image and Detections */}
        <div className="lg:col-span-2 space-y-6">
          {/* Image Viewer */}
          {analysis.image_filename && (
            <ImageViewer
              imageUrl={analysis.image_filename}
              detections={analysis.detections}
              showDetections={true}
              onDetectionClick={handleDetectionClick}
            />
          )}

          {/* Detections Tabs */}
          <Card className="p-6">
            <Tabs defaultValue="all">
              <TabsList>
                <TabsTrigger value="all">
                  Todas ({detectionCount})
                </TabsTrigger>
                <TabsTrigger value="pending">
                  Pendientes ({pendingValidationCount})
                </TabsTrigger>
                <TabsTrigger value="validated">
                  Validadas ({detectionCount - pendingValidationCount})
                </TabsTrigger>
              </TabsList>

              <TabsContent value="all" className="mt-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {analysis.detections.map((detection) => (
                    <DetectionCard
                      key={detection.id}
                      detection={detection}
                      onValidate={canValidate ? handleValidateDetection : undefined}
                      showActions={canValidate}
                    />
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="pending" className="mt-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {analysis.detections
                    .filter(d => d.validation_status === 'pending_validation')
                    .map((detection) => (
                      <DetectionCard
                        key={detection.id}
                        detection={detection}
                        onValidate={canValidate ? handleValidateDetection : undefined}
                        showActions={canValidate}
                      />
                    ))}
                </div>
              </TabsContent>

              <TabsContent value="validated" className="mt-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
              </TabsContent>
            </Tabs>
          </Card>
        </div>

        {/* Right Column - Info and Risk */}
        <div className="space-y-6">
          {/* Risk Assessment */}
          {analysis.risk_assessment && (
            <RiskAssessmentCard assessment={analysis.risk_assessment} />
          )}

          {/* Analysis Info */}
          <Card className="p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Información del Análisis</h3>

            <div className="space-y-4">
              <div>
                <p className="text-xs text-gray-600 mb-1">Estado</p>
                <RiskBadge level={analysis.risk_assessment?.level || 'BAJO'} />
              </div>

              <div>
                <p className="text-xs text-gray-600 mb-1">Modelo Utilizado</p>
                <p className="text-sm font-medium text-gray-900">
                  {analysis.model_used || 'N/A'}
                </p>
              </div>

              <div>
                <p className="text-xs text-gray-600 mb-1">Umbral de Confianza</p>
                <p className="text-sm font-medium text-gray-900">
                  {analysis.confidence_threshold
                    ? `${(analysis.confidence_threshold * 100).toFixed(0)}%`
                    : 'N/A'}
                </p>
              </div>

              <div>
                <p className="text-xs text-gray-600 mb-1">Versión del Servicio</p>
                <p className="text-sm font-medium text-gray-900">
                  {analysis.yolo_service_version || 'N/A'}
                </p>
              </div>

              {analysis.image_taken_at && (
                <div>
                  <p className="text-xs text-gray-600 mb-1 flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    Fecha de Captura
                  </p>
                  <p className="text-sm font-medium text-gray-900">
                    {formatDate(analysis.image_taken_at)}
                  </p>
                </div>
              )}
            </div>
          </Card>

          {/* Location Info */}
          {hasLocation && (
            <Card className="p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <MapPin className="h-5 w-5" />
                Ubicación
              </h3>

              {analysis.location?.latitude && analysis.location?.longitude && (
                <>
                  <div className="space-y-2 mb-4">
                    <div>
                      <p className="text-xs text-gray-600">Coordenadas</p>
                      <p className="text-sm font-medium text-gray-900">
                        {analysis.location.latitude.toFixed(6)}, {analysis.location.longitude.toFixed(6)}
                      </p>
                    </div>

                    {analysis.location.altitude_meters && (
                      <div>
                        <p className="text-xs text-gray-600">Altitud</p>
                        <p className="text-sm font-medium text-gray-900">
                          {analysis.location.altitude_meters.toFixed(0)} m
                        </p>
                      </div>
                    )}

                    {analysis.location.location_source && (
                      <div>
                        <p className="text-xs text-gray-600">Fuente</p>
                        <p className="text-sm font-medium text-gray-900">
                          {analysis.location.location_source}
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Mini Map */}
                  <div className="rounded-lg overflow-hidden border border-gray-200">
                    <HeatMap
                      data={[{
                        latitude: analysis.location.latitude,
                        longitude: analysis.location.longitude,
                        intensity: 1,
                        riskLevel: analysis.risk_assessment?.level || 'BAJO',
                        detectionCount: detectionCount,
                      }]}
                      center={[analysis.location.latitude, analysis.location.longitude]}
                      zoom={15}
                      className="h-48 w-full"
                    />
                  </div>
                </>
              )}
            </Card>
          )}

          {/* Camera Info */}
          {analysis.camera_info && (
            <Card className="p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Información de Cámara</h3>

              <div className="space-y-2">
                {analysis.camera_info.camera_make && (
                  <div>
                    <p className="text-xs text-gray-600">Fabricante</p>
                    <p className="text-sm font-medium text-gray-900">
                      {analysis.camera_info.camera_make}
                    </p>
                  </div>
                )}

                {analysis.camera_info.camera_model && (
                  <div>
                    <p className="text-xs text-gray-600">Modelo</p>
                    <p className="text-sm font-medium text-gray-900">
                      {analysis.camera_info.camera_model}
                    </p>
                  </div>
                )}

                {analysis.camera_info.camera_software && (
                  <div>
                    <p className="text-xs text-gray-600">Software</p>
                    <p className="text-sm font-medium text-gray-900">
                      {analysis.camera_info.camera_software}
                    </p>
                  </div>
                )}
              </div>
            </Card>
          )}
        </div>
      </div>

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
