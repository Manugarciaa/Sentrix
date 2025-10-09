import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Settings, Upload as UploadIcon, Layers, Info } from 'lucide-react'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/Tabs'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Checkbox } from '@/components/ui/Checkbox'
import { Slider } from '@/components/ui/Slider'
import { DropZone } from '@/components/domain/DropZone'
import { ProcessingProgress, ProcessingStep } from '@/components/domain/ProcessingProgress'
import { BatchQueueList } from '@/components/domain/BatchQueueList'
import { useUploadStore } from '@/store/upload'
import { 
  useUploadAnalysis, 
  useBatchUploadAnalyses, 
  useUploadCancellation,
  type UploadProgress,
  type BatchUploadProgress 
} from '@/hooks/useUploadMutations'
import type { AnalysisResult } from '@/types'

const UploadsPage: React.FC = () => {
  const navigate = useNavigate()

  const {
    // Single upload
    currentUpload,
    uploadProgress,
    uploadResult,
    uploadError,
    setCurrentUpload,
    setUploadProgress,
    setUploadResult,
    setUploadError,
    resetUpload,
    // Batch upload
    batchQueue,
    addToBatch,
    removeFromBatch,
    updateBatchItem,
    resetBatch,
    // Config
    config: uploadConfig,
    setConfig,
  } = useUploadStore()

  // React Query mutations
  const uploadAnalysis = useUploadAnalysis()
  const batchUploadAnalyses = useBatchUploadAnalyses()
  const { cancelUpload, cancelAllUploads } = useUploadCancellation()

  const [activeTab, setActiveTab] = useState<'single' | 'batch'>('single')
  const [processingStep, setProcessingStep] = useState<ProcessingStep>('upload')
  const [currentUploadId, setCurrentUploadId] = useState<string | null>(null)
  const [batchProgress, setBatchProgress] = useState<BatchUploadProgress | null>(null)

  useEffect(() => {
    // Reset upload state when component mounts
    resetUpload()
    
    // Cancel any ongoing uploads when component unmounts
    return () => {
      if (currentUploadId) {
        cancelUpload(currentUploadId)
      }
      if (batchUploadAnalyses.isPending) {
        cancelAllUploads()
      }
    }
  }, [])

  // Update processing step based on mutation state
  useEffect(() => {
    if (uploadAnalysis.isPending) {
      setProcessingStep('processing')
    } else if (uploadAnalysis.isSuccess) {
      setProcessingStep('complete')
      setUploadResult(uploadAnalysis.data)
    } else if (uploadAnalysis.isError) {
      setProcessingStep('error')
      setUploadError(uploadAnalysis.error?.message || 'Error desconocido')
    }
  }, [uploadAnalysis.isPending, uploadAnalysis.isSuccess, uploadAnalysis.isError, uploadAnalysis.data, uploadAnalysis.error])

  // Single Upload Handler
  const handleSingleUpload = async (files: File[]) => {
    if (files.length === 0) return

    const file = files[0]
    const uploadId = `single-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    
    setCurrentUpload(file)
    setCurrentUploadId(uploadId)
    setProcessingStep('upload')
    setUploadProgress(0)
    
    // Clear any previous errors
    setUploadError(null)

    // Start upload with progress tracking
    uploadAnalysis.mutate({
      file,
      confidence_threshold: uploadConfig.confidence_threshold || 0.7,
      include_gps: uploadConfig.include_gps !== false,
      onProgress: (progress) => {
        setUploadProgress(progress)
      },
    })
  }

  // Batch Upload Handler
  const handleBatchUpload = async (files: File[]) => {
    if (files.length === 0) return
    addToBatch(files)
  }

  // Process Batch Queue
  const processBatchQueue = async () => {
    const pendingItems = batchQueue.filter(item => item.status === 'pending')
    if (pendingItems.length === 0) return

    // Convert batch items to files array
    const files = pendingItems.map(item => item.file)

    // Start batch upload with progress tracking
    batchUploadAnalyses.mutate({
      files,
      options: {
        confidence_threshold: uploadConfig.confidence_threshold || 0.7,
        include_gps: uploadConfig.include_gps !== false,
      },
      onProgress: (progress: BatchUploadProgress) => {
        setBatchProgress(progress)
        
        // Update individual items in the store
        progress.items.forEach((item) => {
          const batchItem = batchQueue.find(b => b.file.name === item.fileName)
          if (batchItem) {
            updateBatchItem(batchItem.id, {
              status: item.status,
              progress: item.progress,
              error: item.error,
            })
          }
        })
      },
      onItemProgress: (itemId: string, itemProgress: UploadProgress) => {
        // Find the corresponding batch item and update it
        const batchItem = batchQueue.find(b => b.file.name === itemProgress.fileName)
        if (batchItem) {
          updateBatchItem(batchItem.id, {
            status: itemProgress.status,
            progress: itemProgress.progress,
            error: itemProgress.error,
          })
        }
      },
    })
  }

  // Handle batch upload completion
  useEffect(() => {
    if (batchUploadAnalyses.isSuccess && batchProgress) {
      // Update completed items with results
      const results = batchUploadAnalyses.data.results
      results.forEach((result) => {
        const batchItem = batchQueue.find(b => b.file.name === result.analysis?.image_filename)
        if (batchItem) {
          updateBatchItem(batchItem.id, {
            status: 'completed',
            progress: 100,
            result: result as AnalysisResult,
          })
        }
      })
      
      // Clear batch progress
      setBatchProgress(null)
    }
  }, [batchUploadAnalyses.isSuccess, batchUploadAnalyses.data, batchProgress])

  // Handle batch upload errors
  useEffect(() => {
    if (batchUploadAnalyses.isError) {
      // Mark all pending items as failed
      const pendingItems = batchQueue.filter(item => item.status === 'pending' || item.status === 'processing')
      pendingItems.forEach((item) => {
        updateBatchItem(item.id, {
          status: 'failed',
          progress: 0,
          error: batchUploadAnalyses.error?.message || 'Error en el procesamiento por lotes',
        })
      })
      
      // Clear batch progress
      setBatchProgress(null)
    }
  }, [batchUploadAnalyses.isError, batchUploadAnalyses.error])

  const handleViewResult = () => {
    if (uploadResult?.analysis?.id) {
      navigate(`/app/analysis/${uploadResult.analysis.id}`)
    }
  }

  const handleNewUpload = () => {
    // Cancel current upload if in progress
    if (currentUploadId && uploadAnalysis.isPending) {
      cancelUpload(currentUploadId)
    }
    
    // Reset states
    resetUpload()
    setProcessingStep('upload')
    setCurrentUploadId(null)
    uploadAnalysis.reset()
  }

  const handleClearBatch = () => {
    // Cancel batch upload if in progress
    if (batchUploadAnalyses.isPending) {
      cancelAllUploads()
    }
    
    // Reset states
    resetBatch()
    setBatchProgress(null)
    batchUploadAnalyses.reset()
  }

  const canProcessBatch = batchQueue.length > 0 &&
    batchQueue.some(item => item.status === 'pending') &&
    !batchUploadAnalyses.isPending

  // Determine if single upload is in progress
  const isUploading = uploadAnalysis.isPending

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-gray-900">Subir Imágenes</h1>
        <p className="text-base text-gray-700 mt-2">
          Analiza imágenes para detectar criaderos de mosquitos con IA
        </p>
      </div>

      {/* Configuration Card */}
      <Card className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <Settings className="h-5 w-5 text-gray-700" />
          <h2 className="text-lg font-bold text-gray-900">Configuración del Análisis</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Confidence Threshold */}
          <div>
            <Slider
              label="Umbral de Confianza"
              value={(uploadConfig.confidence_threshold || 0.7) * 100}
              onChange={(value) => setConfig({ confidence_threshold: value / 100 })}
              min={50}
              max={95}
              step={5}
              showValue={true}
              formatValue={(v) => `${v.toFixed(0)}%`}
            />
            <p className="text-xs text-gray-600 mt-2">
              Mayor umbral = menos detecciones pero más precisas
            </p>
          </div>

          {/* Options */}
          <div className="space-y-3">
            <Checkbox
              label="Incluir datos GPS"
              description="Extraer coordenadas de los metadatos de la imagen"
              checked={uploadConfig.include_gps !== false}
              onChange={(checked) => setConfig({ include_gps: checked })}
            />
            <Checkbox
              label="Generar recomendaciones automáticas"
              description="Obtener sugerencias basadas en el análisis"
              checked={uploadConfig.auto_recommendations !== false}
              onChange={(checked) => setConfig({ auto_recommendations: checked })}
            />
          </div>
        </div>

        {/* Info Banner */}
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg flex items-start gap-2">
          <Info className="h-5 w-5 text-blue-600 shrink-0 mt-0.5" />
          <p className="text-sm text-blue-900">
            Las imágenes deben ser JPG o PNG, con un tamaño máximo de 10MB.
            Para mejores resultados, usa imágenes con buena iluminación y enfoque nítido.
          </p>
        </div>
      </Card>

      {/* Upload Tabs */}
      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as 'single' | 'batch')}>
        <TabsList>
          <TabsTrigger value="single" className="gap-2">
            <UploadIcon className="h-4 w-4" />
            Imagen Individual
          </TabsTrigger>
          <TabsTrigger value="batch" className="gap-2">
            <Layers className="h-4 w-4" />
            Análisis por Lote
          </TabsTrigger>
        </TabsList>

        {/* Single Upload Tab */}
        <TabsContent value="single" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Upload Zone */}
            <div>
              {!currentUpload ? (
                <DropZone
                  onFilesSelected={handleSingleUpload}
                  maxSize={10}
                  maxFiles={1}
                  multiple={false}
                  disabled={isUploading}
                />
              ) : (
                <ProcessingProgress
                  step={processingStep}
                  progress={uploadProgress}
                  fileName={currentUpload.name}
                  fileSize={currentUpload.size}
                  processingTime={uploadResult?.analysis?.processing_time_ms}
                  detectionCount={uploadResult?.detections?.length}
                  error={uploadError || undefined}
                />
              )}
            </div>

            {/* Actions & Info */}
            <div className="space-y-4">
              {processingStep === 'complete' && uploadResult && (
                <Card className="p-6 bg-gradient-to-br from-green-50 to-green-100 border-green-200">
                  <h3 className="text-lg font-bold text-green-900 mb-4">
                    ¡Análisis Completado!
                  </h3>

                  <div className="space-y-3 mb-6">
                    <div className="flex justify-between">
                      <span className="text-sm text-green-800">ID de Análisis:</span>
                      <span className="text-sm font-semibold text-green-900">
                        #{uploadResult.analysis?.id?.slice(0, 8)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-green-800">Detecciones:</span>
                      <span className="text-sm font-semibold text-green-900">
                        {uploadResult.detections?.length || 0}
                      </span>
                    </div>
                    {uploadResult.analysis?.processing_time_ms && (
                      <div className="flex justify-between">
                        <span className="text-sm text-green-800">Tiempo:</span>
                        <span className="text-sm font-semibold text-green-900">
                          {(uploadResult.analysis.processing_time_ms / 1000).toFixed(1)}s
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="flex gap-3">
                    <Button
                      onClick={handleViewResult}
                      className="flex-1 bg-gradient-to-r from-primary-600 to-cyan-600"
                    >
                      Ver Detalles
                    </Button>
                    <Button
                      onClick={handleNewUpload}
                      variant="outline"
                    >
                      Nuevo Análisis
                    </Button>
                  </div>
                </Card>
              )}

              {processingStep === 'error' && (
                <Card className="p-6">
                  <div className="text-center mb-4">
                    <h3 className="text-lg font-bold text-red-900 mb-2">
                      Error en el Análisis
                    </h3>
                    <p className="text-sm text-red-800">
                      {uploadError || 'Ocurrió un error desconocido'}
                    </p>
                  </div>
                  <Button
                    onClick={handleNewUpload}
                    variant="outline"
                    className="w-full"
                  >
                    Intentar de Nuevo
                  </Button>
                </Card>
              )}

              {(!currentUpload || processingStep === 'upload') && (
                <Card className="p-6">
                  <h3 className="text-lg font-bold text-gray-900 mb-4">
                    ¿Cómo funciona?
                  </h3>
                  <ol className="space-y-3 text-sm text-gray-700">
                    <li className="flex items-start gap-2">
                      <span className="font-semibold text-primary-600 shrink-0">1.</span>
                      <span>Sube una imagen desde tu dispositivo</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-semibold text-primary-600 shrink-0">2.</span>
                      <span>Nuestro modelo de IA analiza la imagen</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-semibold text-primary-600 shrink-0">3.</span>
                      <span>Detecta criaderos de mosquitos y evalúa el riesgo</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-semibold text-primary-600 shrink-0">4.</span>
                      <span>Visualiza resultados detallados y recomendaciones</span>
                    </li>
                  </ol>
                </Card>
              )}
            </div>
          </div>
        </TabsContent>

        {/* Batch Upload Tab */}
        <TabsContent value="batch" className="mt-6">
          <div className="space-y-6">
            {/* Drop Zone for Batch */}
            <DropZone
              onFilesSelected={handleBatchUpload}
              maxSize={10}
              maxFiles={20}
              multiple={true}
              disabled={batchUploadAnalyses.isPending}
            />

            {/* Batch Queue */}
            {batchQueue.length > 0 && (
              <>
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-bold text-gray-900">
                    Cola de Procesamiento
                  </h3>
                  <div className="flex gap-3">
                    <Button
                      onClick={handleClearBatch}
                      variant="outline"
                      size="sm"
                      disabled={batchUploadAnalyses.isPending}
                    >
                      Limpiar Todo
                    </Button>
                    <Button
                      onClick={processBatchQueue}
                      disabled={!canProcessBatch}
                      className="bg-gradient-to-r from-primary-600 to-cyan-600"
                      size="sm"
                    >
                      {batchUploadAnalyses.isPending ? 'Procesando...' : 'Procesar Cola'}
                    </Button>
                  </div>
                </div>

                <BatchQueueList
                  items={batchQueue}
                  onRemove={removeFromBatch}
                />
              </>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default UploadsPage
