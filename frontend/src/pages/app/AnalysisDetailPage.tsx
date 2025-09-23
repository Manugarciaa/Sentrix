import React from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { analysesApi } from '@/api/analyses'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge, getRiskLevelBadge } from '@/components/ui/Badge'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import {
  ArrowLeft,
  MapPin,
  Camera,
  Clock,
  FileImage,
  Target,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Download,
  Zap
} from 'lucide-react'

const AnalysisDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const { data: analysis, isLoading, error } = useQuery({
    queryKey: ['analysis', id],
    queryFn: () => analysesApi.getById(id!),
    enabled: !!id,
  })

  // Debug: Log the analysis data
  React.useEffect(() => {
    if (analysis) {
      console.log('Analysis data received:', analysis)
      console.log('Location data:', analysis.location)
      console.log('Has location:', analysis.location?.has_location)
    }
  }, [analysis])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (error || !analysis) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="mx-auto h-12 w-12 text-red-500 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error al cargar el análisis</h3>
        <p className="text-gray-500 mb-4">No se pudo encontrar la información del análisis solicitado.</p>
        <Button onClick={() => navigate('/app/analysis')} variant="outline">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Volver a Análisis
        </Button>
      </div>
    )
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString('es-PE', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const formatFileSize = (bytes: number) => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    if (bytes === 0) return '0 Bytes'
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button
            onClick={() => navigate('/app/analysis')}
            variant="outline"
            size="sm"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Volver
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Análisis #{analysis.id.split('-')[0]}</h1>
            <p className="text-gray-500 mt-1">
              Procesado el {formatDate(analysis.created_at)}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          {getRiskLevelBadge(analysis.risk_assessment?.level || 'BAJO')}
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              analysesApi.export(analysis.id, 'json')
                .catch(error => {
                  console.error('Error exporting analysis:', error)
                })
            }}
          >
            <Download className="w-4 h-4 mr-2" />
            Exportar JSON
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column - Image and Basic Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Image Analysis */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <FileImage className="w-5 h-5 mr-2" />
                Imagen Analizada
              </CardTitle>
              <CardDescription>
                Vista de la imagen procesada con detecciones marcadas
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="relative bg-gray-100 rounded-lg overflow-hidden min-h-[400px]">
                {analysis.image_filename ? (
                  <div className="relative">
                    <img
                      src={`http://localhost:8002/api/v1/analyses/${analysis.id}/image`}
                      alt={analysis.image_filename}
                      className="w-full h-auto max-h-[500px] object-contain bg-white"
                      onError={(e) => {
                        console.log('Image failed to load:', e)
                        e.currentTarget.style.display = 'none'
                      }}
                    />

                    {/* Detection overlays */}
                    {analysis.detections && analysis.detections.length > 0 && (
                      <div className="absolute inset-0">
                        {analysis.detections.map((detection, index) => (
                          <div
                            key={detection.id || index}
                            className="absolute border-2 border-red-500 bg-red-500 bg-opacity-20"
                            style={{
                              left: `${detection.bbox?.x || 0}%`,
                              top: `${detection.bbox?.y || 0}%`,
                              width: `${detection.bbox?.width || 0}%`,
                              height: `${detection.bbox?.height || 0}%`,
                            }}
                          >
                            <div className="absolute -top-6 left-0 bg-red-500 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                              {detection.class_name} ({(detection.confidence * 100).toFixed(1)}%)
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-[400px]">
                    <div className="text-center">
                      <FileImage className="mx-auto h-16 w-16 text-gray-400 mb-4" />
                      <p className="text-gray-500 mb-2">{analysis.image_filename}</p>
                      <p className="text-sm text-gray-400">
                        {analysis.image_size_bytes ? formatFileSize(analysis.image_size_bytes) : 'Tamaño desconocido'}
                      </p>
                      <p className="text-sm text-blue-600 mt-2">
                        Imagen almacenada - Storage en desarrollo
                      </p>
                      <div className="mt-4 flex justify-center space-x-2">
                        <Badge variant="outline">
                          {analysis.risk_assessment?.total_detections || 0} detecciones
                        </Badge>
                        <Badge variant="outline">
                          {(analysis.processing_time_ms || 0) / 1000}s procesamiento
                        </Badge>
                      </div>
                    </div>
                  </div>
                )}

                {/* Image metadata */}
                <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-60 text-white p-3">
                  <div className="flex justify-between items-center text-sm">
                    <span>{analysis.image_filename}</span>
                    <div className="flex space-x-3">
                      <Badge variant="outline" className="bg-white text-black">
                        {analysis.risk_assessment?.total_detections || 0} detecciones
                      </Badge>
                      <Badge variant="outline" className="bg-white text-black">
                        {(analysis.processing_time_ms || 0) / 1000}s
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Detections */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Target className="w-5 h-5 mr-2" />
                Detecciones Encontradas
              </CardTitle>
              <CardDescription>
                Sitios de cría potenciales identificados por el sistema
              </CardDescription>
            </CardHeader>
            <CardContent>
              {analysis.detections && analysis.detections.length > 0 ? (
                <div className="space-y-4">
                  {analysis.detections.map((detection, index) => (
                    <div key={detection.id || index} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium">{detection.class_name}</h4>
                        <Badge variant="outline">
                          {(detection.confidence * 100).toFixed(1)}% confianza
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">
                        Tipo: {detection.breeding_site_type}
                      </p>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span>Área: {detection.mask_area?.toFixed(2)} px²</span>
                        <span>Riesgo: {detection.risk_level}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <CheckCircle className="mx-auto h-12 w-12 text-green-500 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    No se encontraron sitios de cría
                  </h3>
                  <p className="text-gray-500">
                    Esta imagen no presenta sitios potenciales de cría de Aedes aegypti
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column - Details and Location */}
        <div className="space-y-6">
          {/* Risk Assessment */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="w-5 h-5 mr-2" />
                Evaluación de Riesgo
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-center">
                <div className="text-3xl font-bold mb-2">
                  {getRiskLevelBadge(analysis.risk_assessment?.level || 'BAJO')}
                </div>
                <p className="text-gray-600">Nivel de Riesgo</p>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="text-center p-3 bg-gray-50 rounded">
                  <div className="font-semibold text-lg">
                    {analysis.risk_assessment?.total_detections || 0}
                  </div>
                  <div className="text-gray-600">Total</div>
                </div>
                <div className="text-center p-3 bg-red-50 rounded">
                  <div className="font-semibold text-lg text-red-600">
                    {analysis.risk_assessment?.high_risk_count || 0}
                  </div>
                  <div className="text-gray-600">Alto Riesgo</div>
                </div>
              </div>

              {analysis.risk_assessment?.recommendations && (
                <div>
                  <h4 className="font-medium mb-2">Recomendaciones:</h4>
                  <ul className="space-y-1 text-sm text-gray-600">
                    {analysis.risk_assessment.recommendations.map((rec, index) => (
                      <li key={index} className="flex items-start">
                        <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 mr-2 flex-shrink-0" />
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Technical Details */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Zap className="w-5 h-5 mr-2" />
                Detalles Técnicos
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Estado:</span>
                <Badge variant={analysis.status === 'completed' ? 'default' : 'secondary'}>
                  {analysis.status}
                </Badge>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Modelo:</span>
                <span className="font-medium">{analysis.model_used || 'N/A'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Confianza:</span>
                <span className="font-medium">{(analysis.confidence_threshold || 0) * 100}%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Tiempo:</span>
                <span className="font-medium">
                  {analysis.processing_time_ms ? `${(analysis.processing_time_ms / 1000).toFixed(2)}s` : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Versión YOLO:</span>
                <span className="font-medium">{analysis.yolo_service_version || 'N/A'}</span>
              </div>
            </CardContent>
          </Card>

          {/* Location Info */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <MapPin className="w-5 h-5 mr-2" />
                Información de Ubicación
              </CardTitle>
            </CardHeader>
            <CardContent>
              {analysis.location?.has_location ? (
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Latitud:</span>
                    <span className="font-medium">{analysis.location.latitude}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Longitud:</span>
                    <span className="font-medium">{analysis.location.longitude}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Coordenadas:</span>
                    <span className="font-medium">{analysis.location.coordinates}</span>
                  </div>
                  {analysis.location.altitude_meters && (
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Altitud:</span>
                      <span className="font-medium">{analysis.location.altitude_meters}m</span>
                    </div>
                  )}
                  <div className="pt-3">
                    <Button
                      size="sm"
                      className="w-full"
                      variant="outline"
                      onClick={() => {
                        const url = analysis.location.google_maps_url ||
                                  `https://www.google.com/maps/search/?api=1&query=${analysis.location.latitude},${analysis.location.longitude}`
                        window.open(url, '_blank')
                      }}
                    >
                      <MapPin className="w-4 h-4 mr-2" />
                      Ver en Google Maps
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-4">
                  <MapPin className="mx-auto h-8 w-8 text-gray-400 mb-2" />
                  <p className="text-sm text-gray-500">
                    No hay información de ubicación GPS disponible
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Camera Info */}
          {analysis.camera_info && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Camera className="w-5 h-5 mr-2" />
                  Información de Cámara
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Marca:</span>
                  <span className="font-medium">{analysis.camera_info.camera_make}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Modelo:</span>
                  <span className="font-medium">{analysis.camera_info.camera_model}</span>
                </div>
                {analysis.camera_info.camera_datetime && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Fecha toma:</span>
                    <span className="font-medium">
                      {formatDate(analysis.camera_info.camera_datetime)}
                    </span>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}

export default AnalysisDetailPage