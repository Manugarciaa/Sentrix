import React, { useState, useCallback } from 'react'
import { useQueryClient, useMutation, useQuery } from '@tanstack/react-query'
import { useDropzone } from 'react-dropzone'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge, getRiskLevelBadge } from '@/components/ui/Badge'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { api } from '@/api/client'
import { apiEndpoints } from '@/lib/config'
import { Upload, X, Eye, MapPin, Camera, CheckCircle, AlertCircle, Clock } from 'lucide-react'
// import { useCurrentUser } from '@/store/auth'

interface UploadFile {
  file: File
  preview: string
  id: string
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'error'
  progress: number
  result?: UploadsAnalysisResult
  error?: string
}

interface UploadsAnalysisResult {
  analysis_id: string
  status: string
  has_gps_data: boolean
  camera_detected: string | null
  estimated_processing_time: string
  message: string
}

interface AnalysisListItem {
  id: string
  image_filename: string
  status: string
  risk_assessment: {
    level: string
    total_detections: number
  }
  location: {
    has_location: boolean
    latitude?: number
    longitude?: number
  }
  camera_info?: {
    camera_make: string
    camera_model: string
  }
  created_at: string
}

const UploadsPage: React.FC = () => {
  // const user = useCurrentUser()
  const queryClient = useQueryClient()
  const [uploadFiles, setUploadFiles] = useState<UploadFile[]>([])

  // Fetch recent analyses
  const { data: recentAnalyses, isLoading: analysesLoading } = useQuery({
    queryKey: ['analyses'],
    queryFn: async (): Promise<{ analyses: AnalysisListItem[] }> => {
      return api.get(`${apiEndpoints.analyses.list}?limit=10`)
    },
    refetchInterval: 30000,
  })

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: async ({ file }: { file: File; uploadId: string }): Promise<UploadsAnalysisResult> => {
      return api.uploadAnalysis(
        apiEndpoints.analyses.create,
        file,
        {
          confidenceThreshold: 0.5,
          includeGps: true
        }
      )
    },
    onMutate: ({ uploadId }) => {
      setUploadFiles(prev =>
        prev.map(f =>
          f.id === uploadId
            ? { ...f, status: 'uploading' as const, progress: 0 }
            : f
        )
      )
    },
    onSuccess: (data: UploadsAnalysisResult, { uploadId }) => {
      setUploadFiles(prev =>
        prev.map(f =>
          f.id === uploadId
            ? {
                ...f,
                status: 'completed' as const,
                progress: 100,
                result: data
              }
            : f
        )
      )
      // Refresh analyses list
      queryClient.invalidateQueries({ queryKey: ['analyses'] })
    },
    onError: (error: any, { uploadId }) => {
      setUploadFiles(prev =>
        prev.map(f =>
          f.id === uploadId
            ? {
                ...f,
                status: 'error' as const,
                error: error.message || 'Error processing image'
              }
            : f
        )
      )
    },
  })

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      preview: URL.createObjectURL(file),
      id: Math.random().toString(36).substr(2, 9),
      status: 'pending' as const,
      progress: 0,
    }))

    setUploadFiles(prev => [...prev, ...newFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/tiff': ['.tiff', '.tif'],
    },
    maxSize: 50 * 1024 * 1024, // 50MB
    multiple: true,
  })

  const removeFile = (id: string) => {
    setUploadFiles(prev => {
      const file = prev.find(f => f.id === id)
      if (file?.preview) {
        URL.revokeObjectURL(file.preview)
      }
      return prev.filter(f => f.id !== id)
    })
  }

  const startUpload = (id: string) => {
    const file = uploadFiles.find(f => f.id === id)
    if (file && file.status === 'pending') {
      uploadMutation.mutate({ file: file.file, uploadId: id })
    }
  }

  const startAllUploads = () => {
    uploadFiles
      .filter(f => f.status === 'pending')
      .forEach(f => startUpload(f.id))
  }

  const clearCompleted = () => {
    setUploadFiles(prev => {
      const toRemove = prev.filter(f => f.status === 'completed' || f.status === 'error')
      toRemove.forEach(f => {
        if (f.preview) URL.revokeObjectURL(f.preview)
      })
      return prev.filter(f => f.status !== 'completed' && f.status !== 'error')
    })
  }

  const getStatusIcon = (status: UploadFile['status']) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-4 w-4 text-gray-400" />
      case 'uploading':
      case 'processing':
        return <LoadingSpinner size="sm" />
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      default:
        return null
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString('es-PE', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const pendingCount = uploadFiles.filter(f => f.status === 'pending').length
  const processingCount = uploadFiles.filter(f => ['uploading', 'processing'].includes(f.status)).length

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Subir Imágenes</h1>
        <p className="text-gray-600">
          Carga imágenes para análisis automático de criaderos de dengue
        </p>
      </div>

      {/* Upload Area */}
      <Card>
        <CardHeader>
          <CardTitle>Nueva Carga</CardTitle>
          <CardDescription>
            Arrastra archivos aquí o haz clic para seleccionar. Formatos soportados: JPG, PNG, TIFF (máx. 50MB)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div
            {...getRootProps()}
            className={`
              border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
              ${isDragActive
                ? 'border-blue-400 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
              }
            `}
          >
            <input {...getInputProps()} />
            <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            {isDragActive ? (
              <p className="text-blue-600 text-lg">Suelta las imágenes aquí...</p>
            ) : (
              <div>
                <p className="text-gray-600 text-lg mb-2">
                  Arrastra imágenes aquí o <span className="text-blue-600 font-medium">explora archivos</span>
                </p>
                <p className="text-sm text-gray-500">
                  Admite múltiples archivos • Extracción automática de GPS • Detección de cámara
                </p>
              </div>
            )}
          </div>

          {/* Upload Queue */}
          {uploadFiles.length > 0 && (
            <div className="mt-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium">
                  Cola de Carga ({uploadFiles.length} archivos)
                </h3>
                <div className="flex gap-2">
                  {pendingCount > 0 && (
                    <Button onClick={startAllUploads} disabled={processingCount > 0}>
                      Procesar Todo ({pendingCount})
                    </Button>
                  )}
                  <Button
                    variant="outline"
                    onClick={clearCompleted}
                    disabled={uploadFiles.filter(f => ['completed', 'error'].includes(f.status)).length === 0}
                  >
                    Limpiar Completados
                  </Button>
                </div>
              </div>

              <div className="space-y-3">
                {uploadFiles.map((uploadFile) => (
                  <div
                    key={uploadFile.id}
                    className="flex items-center gap-4 p-4 border rounded-lg bg-gray-50"
                  >
                    {/* Preview */}
                    <div className="flex-shrink-0">
                      <img
                        src={uploadFile.preview}
                        alt="Preview"
                        className="h-16 w-16 object-cover rounded border"
                      />
                    </div>

                    {/* File Info */}
                    <div className="flex-grow min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        {getStatusIcon(uploadFile.status)}
                        <p className="font-medium text-gray-900 truncate">
                          {uploadFile.file.name}
                        </p>
                      </div>
                      <p className="text-sm text-gray-500">
                        {formatFileSize(uploadFile.file.size)}
                      </p>

                      {uploadFile.status === 'uploading' && (
                        <div className="mt-2">
                          <div className="bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full transition-all"
                              style={{ width: `${uploadFile.progress}%` }}
                            />
                          </div>
                        </div>
                      )}

                      {uploadFile.error && (
                        <p className="text-sm text-red-600 mt-1">{uploadFile.error}</p>
                      )}

                      {uploadFile.result && (
                        <div className="mt-2 flex items-center gap-4 text-sm">
                          <span className="text-green-600 font-medium">
                            ✓ Análisis completado
                          </span>
                          {uploadFile.result.has_gps_data && (
                            <span className="flex items-center gap-1 text-blue-600">
                              <MapPin className="h-3 w-3" />
                              GPS detectado
                            </span>
                          )}
                          {uploadFile.result.camera_detected && (
                            <span className="flex items-center gap-1 text-purple-600">
                              <Camera className="h-3 w-3" />
                              {uploadFile.result.camera_detected}
                            </span>
                          )}
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex-shrink-0 flex items-center gap-2">
                      {uploadFile.status === 'pending' && (
                        <Button
                          size="sm"
                          onClick={() => startUpload(uploadFile.id)}
                          disabled={processingCount > 0}
                        >
                          Procesar
                        </Button>
                      )}

                      {uploadFile.result && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => window.open(`/app/analysis/${uploadFile.result?.analysis_id}`, '_blank')}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                      )}

                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => removeFile(uploadFile.id)}
                        disabled={uploadFile.status === 'uploading'}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recent Analyses */}
      <Card>
        <CardHeader>
          <CardTitle>Análisis Recientes</CardTitle>
          <CardDescription>
            Últimos análisis procesados en el sistema
          </CardDescription>
        </CardHeader>
        <CardContent>
          {analysesLoading ? (
            <div className="flex items-center justify-center py-8">
              <LoadingSpinner size="lg" text="Cargando análisis..." />
            </div>
          ) : recentAnalyses?.analyses?.length ? (
            <div className="space-y-3">
              {recentAnalyses.analyses.map((analysis) => (
                <div
                  key={analysis.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer"
                  onClick={() => window.open(`/app/analysis/${analysis.id}`, '_blank')}
                >
                  <div className="flex items-center gap-4">
                    <div className="h-2 w-2 bg-green-500 rounded-full" />
                    <div>
                      <p className="font-medium text-gray-900">
                        {analysis.image_filename}
                      </p>
                      <div className="flex items-center gap-4 text-sm text-gray-500">
                        <span>{formatDate(analysis.created_at)}</span>
                        <span>{analysis.risk_assessment.total_detections} detecciones</span>
                        {analysis.location.has_location && (
                          <span className="flex items-center gap-1">
                            <MapPin className="h-3 w-3" />
                            GPS
                          </span>
                        )}
                        {analysis.camera_info && (
                          <span className="flex items-center gap-1">
                            <Camera className="h-3 w-3" />
                            {analysis.camera_info.camera_make}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={getRiskLevelBadge(analysis.risk_assessment.level) as any}>
                      {analysis.risk_assessment.level}
                    </Badge>
                    <Eye className="h-4 w-4 text-gray-400" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">
              No hay análisis recientes
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default UploadsPage