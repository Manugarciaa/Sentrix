import React, { useState, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Camera, Upload as UploadIcon, CheckCircle, AlertCircle, X, Image as ImageIcon, MapPin, TrendingUp, ExternalLink, Settings, Info } from 'lucide-react'
import heic2any from 'heic2any'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Checkbox } from '@/components/ui/Checkbox'
import { Slider } from '@/components/ui/Slider'
import { routes, fileConstraints, config, apiEndpoints } from '@/lib/config'
import { showToast } from '@/lib/toast'
import LocationPicker from '@/components/domain/LocationPicker'
import type { Analysis, LocationData } from '@/types'

// ==================== TYPES ====================
interface AnalysisResult extends Partial<Analysis> {
  id: string
  detections: Array<{
    type?: string
    class_name?: string
    confidence: number
    bbox?: [number, number, number, number]
  }>
  risk_level?: string
  risk_assessment?: {
    level?: string
  }
  processed_image_url?: string
  location?: LocationData
  analysis?: {
    id: string
    processing_time_ms?: number
    image_filename?: string
  }
}

type Step = 'upload' | 'preview' | 'analyzing' | 'results'

// ==================== MAIN COMPONENT ====================
const UploadsPage: React.FC = () => {
  const navigate = useNavigate()

  // ========== REFS ==========
  const fileInputRef = useRef<HTMLInputElement>(null)
  const cameraInputRef = useRef<HTMLInputElement>(null)

  // ========== STATE ==========
  const [step, setStep] = useState<Step>('upload')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  // Configuration
  const [confidenceThreshold, setConfidenceThreshold] = useState(50) // 50% (mismo que demo público)
  const [includeGPS, setIncludeGPS] = useState(true)
  const [autoRecommendations, setAutoRecommendations] = useState(true)

  // Manual GPS
  const [showLocationPicker, setShowLocationPicker] = useState(false)
  const [manualLat, setManualLat] = useState<number | null>(null)
  const [manualLng, setManualLng] = useState<number | null>(null)

  // ========== AUTH CHECK ==========
  React.useEffect(() => {
    const token = localStorage.getItem('sentrix_token')
    if (!token) {
      console.error('[AUTH] No authentication token found')
      showToast.error(
        'No autenticado',
        'Debes iniciar sesión para subir imágenes. Redirigiendo...'
      )
      setTimeout(() => {
        navigate('/auth/login?redirect=/app/uploads')
      }, 2000)
    } else {
      console.log('[AUTH] ✓ Authenticated - Token found')
    }
  }, [navigate])

  // ========== FILE VALIDATION ==========
  const validateFile = useCallback((file: File): string | null => {
    let isValidType = fileConstraints.allowedTypes.includes(file.type)

    if (!isValidType || !file.type) {
      const fileName = file.name.toLowerCase()
      const fileExtension = fileName.substring(fileName.lastIndexOf('.'))
      isValidType = fileConstraints.allowedExtensions.includes(fileExtension)
    }

    if (!isValidType) {
      return 'Formato no permitido. Use JPG, PNG, TIFF, HEIC, WebP o BMP.'
    }
    if (file.size > fileConstraints.maxSize) {
      return `Archivo muy grande. Máximo ${fileConstraints.maxSize / (1024 * 1024)}MB.`
    }
    return null
  }, [])

  // ========== FILE HANDLING ==========
  const processFile = useCallback(async (file: File) => {
    const validationError = validateFile(file)
    if (validationError) {
      showToast.error('Archivo inválido', validationError)
      return
    }

    setIsProcessing(true)
    setSelectedFile(null)
    setPreviewUrl(null)
    setAnalysisResult(null)

    // Check if HEIC
    const isHEIC = file.name.toLowerCase().match(/\.(heic|heif)$/)

    if (isHEIC) {
      try {
        showToast.info('Convirtiendo HEIC', 'Procesando archivo...')

        const convertedBlob = await heic2any({
          blob: file,
          toType: 'image/jpeg',
          quality: 0.9
        })

        const blob = Array.isArray(convertedBlob) ? convertedBlob[0] : convertedBlob
        const convertedFile = new File(
          [blob],
          file.name.replace(/\.(heic|heif)$/i, '.jpg'),
          { type: 'image/jpeg' }
        )

        setSelectedFile(convertedFile)
        const reader = new FileReader()
        reader.onload = (e) => {
          setPreviewUrl(e.target?.result as string)
          setStep('preview')
          setIsProcessing(false)
        }
        reader.readAsDataURL(blob)

        showToast.success('Conversión exitosa')
      } catch (err) {
        console.error('HEIC conversion error:', err)
        showToast.error('Error de conversión', 'No se pudo convertir el archivo HEIC.')
        setIsProcessing(false)
      }
    } else {
      setSelectedFile(file)
      const reader = new FileReader()
      reader.onload = (e) => {
        setPreviewUrl(e.target?.result as string)
        setStep('preview')
        setIsProcessing(false)
      }
      reader.readAsDataURL(file)
    }

    // Clear inputs
    if (fileInputRef.current) fileInputRef.current.value = ''
    if (cameraInputRef.current) cameraInputRef.current.value = ''
  }, [validateFile])

  // ========== DRAG & DROP ==========
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback(() => {
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) processFile(file)
  }, [processFile])

  // ========== LOCATION PICKER ==========
  const handleLocationSelect = useCallback((lat: number, lng: number) => {
    setManualLat(lat)
    setManualLng(lng)
    showToast.success('Ubicación configurada', `Lat: ${lat.toFixed(6)}, Lng: ${lng.toFixed(6)}`)
  }, [])

  const handleRemoveManualLocation = useCallback(() => {
    setManualLat(null)
    setManualLng(null)
    showToast.info('Ubicación removida', 'Se usarán los datos GPS de la imagen si existen')
  }, [])

  // ========== ANALYSIS ==========
  const handleAnalyze = useCallback(async () => {
    if (!selectedFile) return

    setStep('analyzing')
    setUploadProgress(0)

    console.log('[UPLOADS] Starting authenticated analysis:', {
      file: selectedFile.name,
      confidence: confidenceThreshold / 100,
      includeGPS,
      manualLocation: manualLat && manualLng ? { lat: manualLat, lng: manualLng } : null
    })

    showToast.info('Analizando imagen', 'Guardando y procesando con IA...')

    try {
      // Step 1: Create analysis with authenticated endpoint (saves to DB)
      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('confidence_threshold', (confidenceThreshold / 100).toString())
      formData.append('include_gps', includeGPS.toString())

      // Add manual GPS coordinates if provided
      if (manualLat !== null && manualLng !== null) {
        formData.append('latitude', manualLat.toString())
        formData.append('longitude', manualLng.toString())
      }

      const token = localStorage.getItem(config.auth.tokenKey)
      if (!token) {
        showToast.error('No autenticado', 'Inicia sesión para continuar')
        setTimeout(() => navigate('/auth/login?redirect=/app/uploads'), 1500)
        return
      }

      const createResponse = await fetch(`${config.api.baseUrl}${apiEndpoints.analyses.create}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,
      })

      if (createResponse.status === 401) {
        showToast.error('Sesión expirada', 'Inicia sesión nuevamente')
        localStorage.removeItem(config.auth.tokenKey)
        setTimeout(() => navigate('/auth/login?redirect=/app/uploads'), 1500)
        return
      }

      if (!createResponse.ok) {
        const errorData = await createResponse.json().catch(() => ({}))
        throw new Error(errorData.message || errorData.detail || `Error ${createResponse.status}`)
      }

      const createData = await createResponse.json()
      const analysisId = createData.analysis_id
      console.log('[UPLOADS] Analysis created:', analysisId)

      setUploadProgress(50)

      // Step 2: Fetch full analysis details
      console.log('[UPLOADS] Fetching analysis details...')
      const detailsResponse = await fetch(
        `${config.api.baseUrl}${apiEndpoints.analyses.detail(analysisId)}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )

      if (!detailsResponse.ok) {
        throw new Error('Error al obtener detalles del análisis')
      }

      const detailsData = await detailsResponse.json()
      console.log('[UPLOADS] Analysis details:', detailsData)

      setUploadProgress(100)

      // Set result data
      setAnalysisResult({
        id: detailsData.id,
        detections: detailsData.detections || [],
        risk_level: detailsData.risk_level,
        risk_assessment: { level: detailsData.risk_level },
        processed_image_url: detailsData.processed_image_url,
        location: detailsData.location || {
          has_location: detailsData.has_gps_data,
          coordinates: detailsData.google_maps_url ?
            detailsData.google_maps_url.replace('https://maps.google.com/?q=', '') : null,
          google_maps_url: detailsData.google_maps_url
        },
        analysis: {
          id: detailsData.id,
          processing_time_ms: detailsData.processing_time_ms,
          image_filename: detailsData.image_filename
        }
      })

      setStep('results')

      const detectionCount = detailsData.detections?.length || 0
      if (detectionCount > 0) {
        showToast.warning(
          `Criadero${detectionCount > 1 ? 's' : ''} detectado${detectionCount > 1 ? 's' : ''}`,
          `Se identificaron ${detectionCount} posible${detectionCount > 1 ? 's' : ''} criadero${detectionCount > 1 ? 's' : ''}. Análisis guardado.`
        )
      } else {
        showToast.success('Análisis completado', 'No se detectaron criaderos. Análisis guardado.')
      }

    } catch (err) {
      console.error('[UPLOADS] Analysis error:', err)
      setStep('preview')
      const errorMessage = err instanceof Error ? err.message : 'No se pudo procesar la imagen'
      showToast.error('Error al analizar', errorMessage)
    }
  }, [selectedFile, confidenceThreshold, includeGPS, navigate])

  // ========== ACTIONS ==========
  const handleReset = useCallback(() => {
    setStep('upload')
    setSelectedFile(null)
    setPreviewUrl(null)
    setAnalysisResult(null)
    setUploadProgress(0)
    setManualLat(null)
    setManualLng(null)
  }, [])

  const handleViewDetails = useCallback(() => {
    const id = analysisResult?.analysis?.id || analysisResult?.id
    if (id) navigate(`${routes.app.analysis}/${id}`)
  }, [analysisResult, navigate])

  // ========== UTILITY FUNCTIONS ==========
  const getRiskColor = (level?: string) => {
    switch (level?.toLowerCase()) {
      case 'critico':
      case 'alto':
        return 'text-red-600 bg-red-50 border-red-200 dark:text-red-400 dark:bg-red-950 dark:border-red-800'
      case 'medio':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200 dark:text-yellow-400 dark:bg-yellow-950 dark:border-yellow-800'
      case 'bajo':
      case 'minimo':
        return 'text-green-600 bg-green-50 border-green-200 dark:text-green-400 dark:bg-green-950 dark:border-green-800'
      default:
        return 'text-muted-foreground bg-muted/20 border-border'
    }
  }

  const getRiskLevel = () => {
    return analysisResult?.risk_assessment?.level || analysisResult?.risk_level || 'N/A'
  }

  // ==================== RENDER ====================
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className={step !== 'upload' ? 'mb-3 sm:mb-4' : 'mb-6 sm:mb-8'}>
        <h1 className={`font-bold tracking-tight text-foreground ${
          step !== 'upload' ? 'text-2xl sm:text-3xl mb-2' : 'text-3xl sm:text-4xl mb-3'
        }`}>
          Subir y Analizar Imágenes
        </h1>
        {step === 'upload' && (
          <p className="text-base text-muted-foreground">
            Sube una imagen o toma una foto para detectar criaderos del mosquito Aedes aegypti
          </p>
        )}
      </div>

      {/* Configuration - Only on upload step */}
      {step === 'upload' && (
        <Card className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <Settings className="h-5 w-5 text-muted-foreground" />
            <h2 className="text-lg font-bold text-foreground">Configuración del Análisis</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Confidence Threshold */}
            <div>
              <Slider
                label="Umbral de Confianza"
                value={confidenceThreshold}
                onChange={setConfidenceThreshold}
                min={50}
                max={95}
                step={5}
                showValue
                formatValue={(v) => `${v}%`}
              />
              <p className="text-xs text-muted-foreground mt-2">
                Mayor umbral = menos detecciones pero más precisas
              </p>
            </div>

            {/* Options */}
            <div className="space-y-3">
              <Checkbox
                label="Incluir datos GPS"
                description="Extraer coordenadas de los metadatos de la imagen"
                checked={includeGPS}
                onChange={setIncludeGPS}
              />
              <Checkbox
                label="Generar recomendaciones automáticas"
                description="Obtener sugerencias basadas en el análisis"
                checked={autoRecommendations}
                onChange={setAutoRecommendations}
              />
            </div>
          </div>

          {/* Info */}
          <div className="mt-4 p-3 bg-status-info-light dark:bg-status-info-bg-light border border-status-info-border rounded-lg flex items-start gap-2">
            <Info className="h-5 w-5 text-status-info-text shrink-0 mt-0.5" />
            <p className="text-sm text-status-info-text">
              Las imágenes deben ser JPG, PNG, TIFF, HEIC, WebP o BMP con un tamaño máximo de 50MB.
              Para mejores resultados, usa imágenes con buena iluminación y enfoque nítido.
            </p>
          </div>
        </Card>
      )}

      {/* Upload Section */}
      {step === 'upload' && !isProcessing && (
        <Card className="p-5 sm:p-7 lg:p-9">
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            className={`border-2 border-dashed rounded-xl p-8 sm:p-10 lg:p-14 text-center transition-all ${
              isDragging
                ? 'border-primary bg-primary/10 scale-[1.01]'
                : 'border-border hover:border-primary/50 hover:bg-muted/20'
            }`}
          >
            <div className="mb-8">
              <div className="mx-auto h-14 w-14 sm:h-18 sm:w-18 rounded-xl bg-gradient-to-br from-primary/20 to-primary/10 flex items-center justify-center mb-4 sm:mb-5 shadow-sm">
                <ImageIcon className="h-7 w-7 sm:h-9 sm:w-9 text-primary" />
              </div>
              <h3 className="text-lg sm:text-xl font-bold text-foreground mb-2">
                {isDragging ? '¡Suelta la imagen aquí!' : 'Sube o arrastra tu imagen'}
              </h3>
              <p className="text-sm sm:text-base text-muted-foreground mb-1.5">
                Formatos soportados: JPG, PNG, TIFF, HEIC, WebP, BMP
              </p>
              <p className="text-sm text-muted-foreground font-medium">
                Tamaño máximo: 50MB
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center max-w-md mx-auto">
              <Button
                onClick={() => cameraInputRef.current?.click()}
                size="lg"
                className="bg-primary hover:bg-primary/90 text-white font-semibold flex-1"
              >
                <Camera className="mr-2 h-5 w-5" />
                Tomar Foto
              </Button>

              <Button
                onClick={() => fileInputRef.current?.click()}
                size="lg"
                variant="outline"
                className="font-semibold border-2 flex-1"
              >
                <UploadIcon className="mr-2 h-5 w-5" />
                Subir Archivo
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Processing */}
      {isProcessing && (
        <Card className="p-10 sm:p-14">
          <div className="text-center">
            <div className="mb-6">
              <div className="animate-spin h-14 w-14 sm:h-16 sm:w-16 border-4 border-muted border-t-primary rounded-full mx-auto"></div>
            </div>
            <h3 className="text-lg sm:text-xl font-bold text-foreground mb-2">
              Procesando Imagen
            </h3>
            <p className="text-sm sm:text-base text-muted-foreground">
              Preparando tu imagen...
            </p>
          </div>
        </Card>
      )}

      {/* Preview */}
      {step === 'preview' && previewUrl && (
        <>
          <Card className="p-5 sm:p-7">
            <div className="flex justify-between items-start mb-5 sm:mb-6">
              <div>
                <h3 className="text-lg sm:text-xl font-bold text-foreground mb-1">Vista Previa</h3>
                <p className="text-sm text-muted-foreground">Verifica tu imagen antes de analizarla</p>
              </div>
              <button
                onClick={handleReset}
                className="p-2 hover:bg-muted rounded-lg transition-all hover:scale-105"
              >
                <X className="h-5 w-5 text-muted-foreground" />
              </button>
            </div>

            <div className="mb-5 sm:mb-6 rounded-xl overflow-hidden border-2 border-border bg-gradient-to-br from-muted/20 to-muted/40">
              <img
                src={previewUrl}
                alt="Preview"
                className="w-full h-auto max-h-[400px] sm:max-h-[500px] object-contain"
              />
            </div>

            {/* Location Section */}
            <div className="mb-5 sm:mb-6">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-bold text-foreground flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-primary" />
                  Ubicación
                </h4>
              </div>

              {manualLat !== null && manualLng !== null ? (
                <div className="p-4 rounded-lg bg-status-success-light dark:bg-status-success-bg-light border border-status-success-border">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-status-success-text mb-1">
                        [OK] Ubicación configurada manualmente
                      </p>
                      <p className="text-sm text-foreground font-mono">
                        Lat: {manualLat.toFixed(6)}, Lng: {manualLng.toFixed(6)}
                      </p>
                    </div>
                    <button
                      onClick={handleRemoveManualLocation}
                      className="p-1.5 hover:bg-muted rounded transition-colors"
                      title="Remover ubicación"
                    >
                      <X className="h-4 w-4 text-muted-foreground" />
                    </button>
                  </div>
                </div>
              ) : (
                <div className="p-4 rounded-lg border-2 border-dashed border-border bg-muted/20">
                  <p className="text-sm text-muted-foreground mb-3">
                    Si la imagen no tiene GPS, puedes agregar la ubicación manualmente
                  </p>
                  <Button
                    onClick={() => setShowLocationPicker(true)}
                    variant="outline"
                    size="sm"
                    className="w-full sm:w-auto"
                  >
                    <MapPin className="h-4 w-4 mr-2" />
                    Agregar Ubicación Manual
                  </Button>
                </div>
              )}
            </div>

            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
              <Button
                onClick={handleAnalyze}
                size="lg"
                className="flex-1 bg-primary hover:bg-primary/90 text-white font-semibold"
                disabled={step === 'analyzing'}
              >
                <CheckCircle className="mr-2 h-5 w-5" />
                Analizar Imagen
              </Button>

              <Button
                onClick={handleReset}
                size="lg"
                variant="outline"
                className="sm:w-auto font-semibold border-2"
              >
                Cancelar
              </Button>
            </div>
          </Card>

          {/* Location Picker Modal */}
          {showLocationPicker && (
            <LocationPicker
              onLocationSelect={handleLocationSelect}
              onClose={() => setShowLocationPicker(false)}
              initialLat={manualLat ?? undefined}
              initialLng={manualLng ?? undefined}
            />
          )}
        </>
      )}

      {/* Analyzing */}
      {step === 'analyzing' && (
        <Card className="p-10 sm:p-14">
          <div className="text-center">
            <div className="mb-6">
              <div className="animate-spin h-14 w-14 sm:h-16 sm:w-16 border-4 border-muted border-t-primary rounded-full mx-auto"></div>
            </div>
            <h3 className="text-lg sm:text-xl font-bold text-foreground mb-2">
              Analizando Imagen
            </h3>
            <p className="text-sm sm:text-base text-muted-foreground mb-4">
              Detectando posibles criaderos del mosquito...
            </p>
            {uploadProgress > 0 && (
              <div className="max-w-xs mx-auto">
                <div className="w-full bg-muted rounded-full h-2">
                  <div
                    className="bg-primary h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
                <p className="text-sm text-muted-foreground mt-2">{uploadProgress}%</p>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Results */}
      {step === 'results' && analysisResult && (
        <div className="space-y-4 sm:space-y-5">
          <Card className="p-5 sm:p-7">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h3 className="text-lg sm:text-xl font-bold text-foreground mb-1">Resultados del Análisis</h3>
                <p className="text-sm text-muted-foreground">Detección completada exitosamente</p>
              </div>
              <button
                onClick={handleReset}
                className="p-2 hover:bg-muted rounded-lg transition-all hover:scale-105"
              >
                <X className="h-5 w-5 text-muted-foreground" />
              </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 sm:gap-6">
              {/* Image */}
              {(analysisResult.processed_image_url || previewUrl) && (
                <div className="rounded-xl border-2 border-border overflow-hidden bg-gradient-to-br from-muted/20 to-muted/40 h-fit">
                  <img
                    src={analysisResult.processed_image_url || previewUrl || ''}
                    alt="Analysis result"
                    className="w-full h-auto max-h-[400px] sm:max-h-[450px] lg:max-h-[500px] object-contain"
                  />
                </div>
              )}

              {/* Stats */}
              <div className="space-y-4">
                {/* Risk, Confidence, Detections */}
                <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-1 xl:grid-cols-3 gap-3">
                  <div className={`p-4 sm:p-5 rounded-xl border-2 ${getRiskColor(getRiskLevel())}`}>
                    <p className="text-xs uppercase tracking-wider mb-2 font-semibold opacity-80">Nivel de Riesgo</p>
                    <p className="text-2xl sm:text-3xl font-bold capitalize">{getRiskLevel()}</p>
                  </div>

                  <div className="p-4 sm:p-5 rounded-xl bg-gradient-to-br from-muted/40 to-muted/20 border-2 border-border">
                    <p className="text-xs text-muted-foreground uppercase tracking-wider mb-2 font-semibold">Confianza</p>
                    <p className="text-2xl sm:text-3xl font-bold text-foreground">
                      {analysisResult.detections && analysisResult.detections.length > 0
                        ? `${Math.round((analysisResult.detections.reduce((sum, d) => sum + d.confidence, 0) / analysisResult.detections.length) * 100)}%`
                        : 'N/A'}
                    </p>
                  </div>

                  <div className="p-4 sm:p-5 rounded-xl bg-gradient-to-br from-primary/5 to-primary/10 border-2 border-primary/20">
                    <p className="text-xs text-primary/80 dark:text-primary uppercase tracking-wider mb-2 font-semibold">Detecciones</p>
                    <p className="text-2xl sm:text-3xl font-bold text-primary">
                      {analysisResult.detections?.length || 0}
                    </p>
                  </div>
                </div>

                {/* Detections Summary */}
                {analysisResult.detections && analysisResult.detections.length > 0 && (
                  <div className="p-4 sm:p-5 rounded-xl bg-gradient-to-br from-card to-muted/20 border-2 border-border">
                    <h4 className="text-sm font-bold text-foreground mb-3 flex items-center gap-2">
                      <TrendingUp className="h-4 w-4 text-primary" />
                      Resumen de Detecciones
                    </h4>
                    <div className="space-y-2.5">
                      {(() => {
                        const grouped = analysisResult.detections.reduce((acc, det) => {
                          const key = det.class_name || det.type || 'Desconocido'
                          acc[key] = (acc[key] || 0) + 1
                          return acc
                        }, {} as Record<string, number>)

                        return Object.entries(grouped).map(([type, count]) => (
                          <div key={type} className="flex justify-between items-center p-2.5 rounded-lg bg-muted/40">
                            <span className="text-sm font-semibold text-foreground">{type}</span>
                            <span className="text-sm font-bold text-primary bg-primary/10 px-3 py-1 rounded-full">×{count}</span>
                          </div>
                        ))
                      })()}
                    </div>
                  </div>
                )}

                {/* Location */}
                {analysisResult.location?.has_location ? (
                  <div className="p-4 sm:p-5 rounded-xl bg-gradient-to-br from-card to-muted/20 border-2 border-border">
                    <h4 className="text-sm font-bold text-foreground mb-3 flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-primary" />
                      Ubicación GPS
                    </h4>
                    <div className="space-y-2.5">
                      {analysisResult.location.coordinates && (
                        <div className="p-2.5 rounded-lg bg-muted/40">
                          <p className="text-xs text-muted-foreground font-semibold mb-1">Coordenadas</p>
                          <p className="text-sm text-foreground font-mono break-all">
                            {analysisResult.location.coordinates}
                          </p>
                        </div>
                      )}
                      {analysisResult.location.google_maps_url && (
                        <a
                          href={analysisResult.location.google_maps_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-2 text-sm font-semibold text-primary hover:text-primary/80 transition-colors"
                        >
                          Ver en Google Maps
                          <ExternalLink className="h-3.5 w-3.5" />
                        </a>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="p-4 sm:p-5 rounded-xl bg-muted/20 border-2 border-dashed border-border">
                    <div className="flex items-center gap-2 mb-2">
                      <MapPin className="h-4 w-4 text-muted-foreground" />
                      <h4 className="text-sm font-bold text-foreground">Ubicación GPS</h4>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      No se detectó información de ubicación en la imagen.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </Card>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
            <Button
              onClick={() => fileInputRef.current?.click()}
              size="lg"
              className="flex-1 bg-primary hover:bg-primary/90 text-white font-semibold"
            >
              <UploadIcon className="mr-2 h-5 w-5" />
              Analizar Otra Imagen
            </Button>

            <Button
              onClick={handleViewDetails}
              size="lg"
              variant="outline"
              className="flex-1 font-semibold border-2"
            >
              Ver Detalles Completos
            </Button>
          </div>
        </div>
      )}

      {/* Hidden inputs */}
      <input
        ref={fileInputRef}
        type="file"
        accept={fileConstraints.allowedTypes.join(',')}
        onChange={(e) => e.target.files?.[0] && processFile(e.target.files[0])}
        className="hidden"
      />

      <input
        ref={cameraInputRef}
        type="file"
        accept="image/*,.heic,.heif"
        capture="environment"
        onChange={(e) => e.target.files?.[0] && processFile(e.target.files[0])}
        className="hidden"
      />
    </div>
  )
}

export default UploadsPage
