import React, { useState, useRef, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { Link } from 'react-router-dom'
import { Camera, Upload, CheckCircle, AlertCircle, X, Image as ImageIcon, MapPin, TrendingUp, ExternalLink, Settings, Info } from 'lucide-react'
import heic2any from 'heic2any'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Slider } from '@/components/ui/Slider'
import { Checkbox } from '@/components/ui/Checkbox'
import { SkeletonImagePreview, SkeletonAnalysisResults } from '@/components/ui/custom-skeletons'
import { routes, config, apiEndpoints, fileConstraints } from '@/lib/config'
import { showToast } from '@/lib/toast'
import type { Analysis, LocationData } from '@/types'

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
}

type UploadStep = 'upload' | 'preview' | 'analyzing' | 'results'

const ReportPage: React.FC = () => {
  const [step, setStep] = useState<UploadStep>('upload')
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [showInfoBanner, setShowInfoBanner] = useState(true)
  const [showUploadMenu, setShowUploadMenu] = useState(false)
  const [isProcessingImage, setIsProcessingImage] = useState(false)
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.7)
  const [includeGPS, setIncludeGPS] = useState(true)

  const fileInputRef = useRef<HTMLInputElement>(null)
  const cameraInputRef = useRef<HTMLInputElement>(null)
  const uploadMenuRef = useRef<HTMLDivElement>(null)

  // Auto-hide info banner after 5 seconds
  useEffect(() => {
    const timer = setTimeout(() => {
      setShowInfoBanner(false)
    }, 5000)
    return () => clearTimeout(timer)
  }, [])

  // Close upload menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (uploadMenuRef.current && !uploadMenuRef.current.contains(event.target as Node)) {
        setShowUploadMenu(false)
      }
    }

    if (showUploadMenu) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showUploadMenu])

  const validateFile = (file: File): string | null => {
    // Check by MIME type first
    let isValidType = fileConstraints.allowedTypes.includes(file.type)

    // If MIME type doesn't match, check by extension (important for HEIC/HEIF)
    if (!isValidType || !file.type) {
      const fileName = file.name.toLowerCase()
      const fileExtension = fileName.substring(fileName.lastIndexOf('.'))
      isValidType = fileConstraints.allowedExtensions.includes(fileExtension)
    }

    if (!isValidType) {
      return 'Formato de archivo no permitido. Use JPG, PNG, TIFF, HEIC, HEIF, WebP o BMP.'
    }
    if (file.size > fileConstraints.maxSize) {
      return 'El archivo es demasiado grande. Máximo 50MB.'
    }
    return null
  }

  const handleFileSelect = async (file: File) => {
    const validationError = validateFile(file)
    if (validationError) {
      setError(validationError)
      setStep('upload')
      return
    }

    // Reset previous states when a new file is actually selected
    setSelectedImage(null)
    setImagePreview(null)
    setAnalysisResult(null)
    setError(null)
    setIsProcessingImage(true)

    // Check if file is HEIC/HEIF
    const isHEIC = file.name.toLowerCase().match(/\.(heic|heif)$/)

    if (isHEIC) {
      try {
        // Convert HEIC to JPEG for preview
        showToast.info(
          'Convirtiendo imagen HEIC',
          'Procesando el archivo para previsualización...',
          { duration: 3000 }
        )

        const convertedBlob = await heic2any({
          blob: file,
          toType: 'image/jpeg',
          quality: 0.9
        })

        // Handle both single blob and array of blobs
        const blob = Array.isArray(convertedBlob) ? convertedBlob[0] : convertedBlob

        // Create a new File object with the converted blob, keeping original name but changing extension
        const convertedFile = new File(
          [blob],
          file.name.replace(/\.(heic|heif)$/i, '.jpg'),
          { type: 'image/jpeg' }
        )

        // Use the converted file for upload
        setSelectedImage(convertedFile)

        // Create preview from converted blob
        const reader = new FileReader()
        reader.onload = (e) => {
          setImagePreview(e.target?.result as string)
          setStep('preview')
          setIsProcessingImage(false)
        }
        reader.onerror = () => {
          setError('Error al leer el archivo convertido')
          setStep('upload')
          setIsProcessingImage(false)
        }
        reader.readAsDataURL(blob)

        showToast.success(
          'Conversión completada',
          'La imagen HEIC ha sido convertida exitosamente.',
          { duration: 2000 }
        )
      } catch (err) {
        console.error('Error converting HEIC:', err)
        setError('Error al convertir archivo HEIC. Por favor, intenta con otro formato.')
        setStep('upload')
        setIsProcessingImage(false)
        showToast.error(
          'Error de conversión',
          'No se pudo convertir el archivo HEIC. Intenta con JPG o PNG.',
          { duration: 5000 }
        )
      }
    } else {
      // For other formats, read and preview normally
      setSelectedImage(file)
      const reader = new FileReader()
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string)
        setStep('preview')
        setIsProcessingImage(false)
      }
      reader.onerror = () => {
        setError('Error al leer el archivo')
        setStep('upload')
        setIsProcessingImage(false)
      }
      reader.readAsDataURL(file)
    }

    // Clear the input value so the same file can be selected again
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
    if (cameraInputRef.current) {
      cameraInputRef.current.value = ''
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleAnalyze = async () => {
    if (!selectedImage) return

    setStep('analyzing')
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', selectedImage)
      // Add configuration parameters
      formData.append('confidence_threshold', confidenceThreshold.toString())
      formData.append('include_gps', includeGPS.toString())

      console.log('[DEBUG] Analyzing image:')
      console.log('  - Endpoint:', `${config.api.baseUrl}${apiEndpoints.upload.image}`)
      console.log('  - Confidence:', confidenceThreshold)
      console.log('  - Include GPS:', includeGPS)
      console.log('  - File:', selectedImage.name, selectedImage.size, 'bytes')

      const response = await fetch(`${config.api.baseUrl}${apiEndpoints.upload.image}`, {
        method: 'POST',
        body: formData,
        // Don't set Content-Type header - browser will set it automatically with boundary
      })

      console.log('Response status:', response.status)

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        console.error('Error response:', errorData)
        throw new Error(errorData.error?.message || 'Error al procesar la imagen')
      }

      const result = await response.json()
      console.log('Analysis result:', result)
      setAnalysisResult(result)
      setStep('results')

      // Show success toast with detection count
      const detectionCount = result.detections?.length || 0
      showToast.success('¡Análisis completado!',
        detectionCount > 0
          ? `Se detectaron ${detectionCount} posible${detectionCount > 1 ? 's' : ''} criadero${detectionCount > 1 ? 's' : ''}.`
          : 'No se detectaron criaderos en esta imagen.',
        { duration: 4000 }
      )
    } catch (err) {
      console.error('Analysis error:', err)
      const errorMessage = err instanceof Error ? err.message : 'Error al analizar la imagen'
      setError(errorMessage)
      setStep('preview')

      // Show error toast
      showToast.error('Error al analizar imagen', errorMessage, { duration: 5000 })
    }
  }

  const handleReset = () => {
    setStep('upload')
    setSelectedImage(null)
    setImagePreview(null)
    setAnalysisResult(null)
    setError(null)
  }

  const handleAnalyzeAnother = () => {
    // Don't reset to upload screen, just toggle the menu
    setShowUploadMenu(!showUploadMenu)
  }

  const handleSelectNewImage = (inputType: 'file' | 'camera') => {
    // Close menu first
    setShowUploadMenu(false)

    // Don't reset states here - only reset when a file is actually selected
    // This prevents the UI from becoming empty if user cancels the file dialog

    // Trigger appropriate input immediately
    if (inputType === 'camera') {
      cameraInputRef.current?.click()
    } else {
      fileInputRef.current?.click()
    }
  }

  const getRiskColor = (riskLevel?: string) => {
    const level = riskLevel?.toLowerCase()
    switch (level) {
      case 'critico':
      case 'alto':
        return 'text-red-600 bg-red-50 border-red-200 dark:text-red-400 dark:bg-red-950 dark:border-red-800'
      case 'medio':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200 dark:text-yellow-400 dark:bg-yellow-950 dark:border-yellow-800'
      case 'bajo':
      case 'minimo':
        return 'text-green-600 bg-green-50 border-green-200 dark:text-green-400 dark:bg-green-950 dark:border-green-800'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200 dark:text-gray-400 dark:bg-gray-900 dark:border-gray-700'
    }
  }

  const getRiskLevel = (result: AnalysisResult): string => {
    return result.risk_assessment?.level || result.risk_level || 'N/A'
  }

  return (
    <>
      {/* Info Banner - Rendered via Portal to stay truly fixed */}
      {showInfoBanner && createPortal(
        <div
          className="fixed-banner"
          style={{
            position: 'fixed',
            top: '5rem',
            right: '1rem',
            left: '1rem',
            zIndex: 9999,
          }}
        >
          <div className="flex justify-end">
            <div className="w-full sm:w-auto sm:max-w-md">
              <div className="bg-status-warning-light dark:bg-status-warning-bg-light border-2 border-status-warning-border dark:border-status-warning-border rounded-lg shadow-lg p-2.5 sm:p-3">
                <div className="flex items-start gap-2">
                  <AlertCircle className="h-4 w-4 text-status-warning-text dark:text-status-warning-text flex-shrink-0 mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-foreground dark:text-foreground">
                      <span className="font-semibold">Modo Demostración:</span> Los resultados no se guardarán.{' '}
                      <Link to={routes.public.register} className="text-status-warning-text dark:text-status-warning-text underline hover:text-status-warning dark:hover:text-status-warning font-medium">
                        Crea una cuenta
                      </Link> para guardarlos.
                    </p>
                  </div>
                  <button
                    onClick={() => setShowInfoBanner(false)}
                    className="p-0.5 hover:bg-status-warning-border dark:hover:bg-status-warning-border/50 rounded transition-colors flex-shrink-0"
                    aria-label="Cerrar aviso"
                  >
                    <X className="h-3.5 w-3.5 text-status-warning-text dark:text-status-warning-text" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>,
        document.body
      )}

      <div className="flex flex-col min-h-screen bg-background">
        {/* Hero Section */}
      <section className="relative flex items-center pt-14 pb-10 sm:pt-16 sm:pb-12">
        <div className={`mx-auto px-4 sm:px-6 lg:px-8 w-full transition-all ${
          step === 'results' ? 'max-w-7xl' : 'max-w-4xl'
        }`}>
          <div className={`text-center transition-all ${
            step !== 'upload' ? 'mb-3 sm:mb-4' : 'mb-6 sm:mb-8'
          }`}>
            <h1 className={`font-bold tracking-tight text-gray-900 dark:text-foreground font-akira leading-tight px-2 transition-all ${
              step !== 'upload'
                ? 'text-2xl sm:text-3xl mb-2 sm:mb-3'
                : 'text-3xl sm:text-4xl md:text-5xl lg:text-6xl mb-3 sm:mb-4'
            }`}>
              Detector de{step !== 'upload' ? ' ' : <br />}
              <span className="text-primary-600 dark:text-primary">Criaderos</span>
            </h1>

            {step === 'upload' && (
              <p className="mx-auto max-w-2xl text-sm sm:text-base leading-relaxed text-gray-700 dark:text-muted-foreground mb-4 sm:mb-6 px-4">
                Sube una imagen o toma una foto para analizar posibles criaderos del mosquito Aedes aegypti.
              </p>
            )}
          </div>

          {/* Configuration Card - Only show on upload step */}
          {step === 'upload' && (
            <Card className="p-6 mb-6">
              <div className="flex items-center gap-2 mb-4">
                <Settings className="h-5 w-5 text-muted-foreground" />
                <h2 className="text-lg font-bold text-foreground">Configuración del Análisis</h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Confidence Threshold */}
                <div>
                  <Slider
                    label="Umbral de Confianza"
                    value={confidenceThreshold * 100}
                    onChange={(value) => setConfidenceThreshold(value / 100)}
                    min={50}
                    max={95}
                    step={5}
                    showValue={true}
                    formatValue={(v) => `${v.toFixed(0)}%`}
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
                    onChange={(checked) => setIncludeGPS(checked)}
                  />
                  <div className="p-3 bg-muted/30 rounded-lg border border-border">
                    <p className="text-xs text-muted-foreground">
                      💡 <strong>Tip:</strong> Para usuarios registrados se incluyen recomendaciones automáticas y acceso a historial completo.
                    </p>
                  </div>
                </div>
              </div>

              {/* Info Banner */}
              <div className="mt-4 p-3 bg-status-info-light dark:bg-status-info-bg-light border border-status-info-border rounded-lg flex items-start gap-2">
                <Info className="h-5 w-5 text-status-info-text shrink-0 mt-0.5" />
                <p className="text-sm text-status-info-text dark:text-status-info-text">
                  Las imágenes deben ser JPG, PNG, TIFF, HEIC, WebP o BMP con un tamaño máximo de 50MB.
                  Para mejores resultados, usa imágenes con buena iluminación y enfoque nítido.
                </p>
              </div>
            </Card>
          )}

          {/* Upload Section */}
          {step === 'upload' && !isProcessingImage && (
            <div className="bg-card rounded-xl border border-border shadow-sm p-5 sm:p-7 lg:p-9">
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
                    className="bg-primary hover:bg-primary/90 text-white font-semibold shadow-sm hover:shadow transition-all flex-1"
                  >
                    <Camera className="mr-2 h-5 w-5" />
                    Tomar Foto
                  </Button>

                  <Button
                    onClick={() => fileInputRef.current?.click()}
                    size="lg"
                    variant="outline"
                    className="font-semibold border-2 hover:bg-muted/50 transition-all flex-1"
                  >
                    <Upload className="mr-2 h-5 w-5" />
                    Subir Archivo
                  </Button>
                </div>
              </div>

              {error && (
                <div className="mt-5 p-4 bg-destructive/10 border-2 border-destructive/20 rounded-xl flex items-start gap-3 shadow-sm">
                  <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0 mt-0.5" />
                  <p className="text-sm font-medium text-destructive">{error}</p>
                </div>
              )}
            </div>
          )}

          {/* Processing Image Section - Show skeleton */}
          {isProcessingImage && (
            <SkeletonImagePreview />
          )}

          {/* Preview Section */}
          {step === 'preview' && imagePreview && (
            <div className="bg-card rounded-xl border border-border shadow-sm p-5 sm:p-7">
              <div className="flex justify-between items-start mb-5 sm:mb-6">
                <div className="flex-1 pr-2">
                  <h3 className="text-lg sm:text-xl font-bold text-foreground mb-1">Vista Previa</h3>
                  <p className="text-sm text-muted-foreground">Verifica tu imagen antes de analizarla</p>
                </div>
                <button
                  onClick={handleReset}
                  className="p-2 hover:bg-muted rounded-lg transition-all hover:scale-105 flex-shrink-0"
                  aria-label="Cancelar"
                >
                  <X className="h-5 w-5 text-muted-foreground" />
                </button>
              </div>

              <div className="mb-5 sm:mb-6 rounded-xl overflow-hidden border-2 border-border bg-gradient-to-br from-muted/20 to-muted/40 shadow-sm">
                <img
                  src={imagePreview}
                  alt="Preview"
                  className="w-full h-auto max-h-[400px] sm:max-h-[500px] object-contain"
                />
              </div>

              <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
                <Button
                  onClick={handleAnalyze}
                  size="lg"
                  className="flex-1 bg-primary hover:bg-primary/90 text-white font-semibold shadow-sm hover:shadow transition-all"
                >
                  <CheckCircle className="mr-2 h-5 w-5" />
                  Analizar Imagen
                </Button>

                <Button
                  onClick={handleReset}
                  size="lg"
                  variant="outline"
                  className="sm:w-auto font-semibold border-2 hover:bg-muted/50 transition-all"
                >
                  Cancelar
                </Button>
              </div>

              {error && (
                <div className="mt-5 p-4 bg-destructive/10 border-2 border-destructive/20 rounded-xl flex items-start gap-3 shadow-sm">
                  <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0 mt-0.5" />
                  <p className="text-sm font-medium text-destructive">{error}</p>
                </div>
              )}
            </div>
          )}

          {/* Analyzing Section - Show skeleton */}
          {step === 'analyzing' && (
            <SkeletonAnalysisResults />
          )}

          {/* Results Section - Optimized Wide Layout */}
          {step === 'results' && analysisResult && (
            <div className="space-y-4 sm:space-y-5">
              <div className="bg-card rounded-xl border border-border shadow-sm p-5 sm:p-7">
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h3 className="text-lg sm:text-xl font-bold text-foreground mb-1">Resultados del Análisis</h3>
                    <p className="text-sm text-muted-foreground">Detección completada exitosamente</p>
                  </div>
                  <button
                    onClick={handleReset}
                    className="p-2 hover:bg-muted rounded-lg transition-all hover:scale-105 flex-shrink-0"
                    aria-label="Cerrar resultados"
                  >
                    <X className="h-5 w-5 text-muted-foreground" />
                  </button>
                </div>

                {/* Side-by-side layout on large screens */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 sm:gap-6">
                  {/* LEFT: Image with detections - Limited height for better layout */}
                  {(analysisResult.processed_image_url || imagePreview) && (
                    <div className="rounded-xl border-2 border-border overflow-hidden bg-gradient-to-br from-muted/20 to-muted/40 shadow-sm h-fit">
                      <img
                        src={analysisResult.processed_image_url || imagePreview || undefined}
                        alt="Analysis result"
                        className="w-full h-auto max-h-[400px] sm:max-h-[450px] lg:max-h-[500px] object-contain"
                      />
                    </div>
                  )}

                  {/* RIGHT: All data panels */}
                  <div className="space-y-4">
                    {/* Stats Panel */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-1 xl:grid-cols-3 gap-3">
                      {/* Risk Level */}
                      <div className={`p-4 sm:p-5 rounded-xl border-2 shadow-sm transition-all hover:shadow-md ${getRiskColor(getRiskLevel(analysisResult))}`}>
                        <p className="text-xs uppercase tracking-wider mb-2 font-semibold opacity-80">Nivel de Riesgo</p>
                        <p className="text-2xl sm:text-3xl font-bold capitalize leading-none">
                          {getRiskLevel(analysisResult)}
                        </p>
                      </div>

                      {/* Average Confidence */}
                      <div className="p-4 sm:p-5 rounded-xl bg-gradient-to-br from-muted/40 to-muted/20 border-2 border-border shadow-sm transition-all hover:shadow-md">
                        <p className="text-xs text-muted-foreground uppercase tracking-wider mb-2 font-semibold">Confianza</p>
                        <p className="text-2xl sm:text-3xl font-bold text-foreground leading-none">
                          {analysisResult.detections && analysisResult.detections.length > 0
                            ? `${Math.round(
                                (analysisResult.detections.reduce((sum, d) => sum + d.confidence, 0) /
                                  analysisResult.detections.length) *
                                  100
                              )}%`
                            : 'N/A'}
                        </p>
                      </div>

                      {/* Total Detections */}
                      <div className="p-4 sm:p-5 rounded-xl bg-gradient-to-br from-primary/5 to-primary/10 border-2 border-primary/20 shadow-sm transition-all hover:shadow-md">
                        <p className="text-xs text-primary/80 uppercase tracking-wider mb-2 font-semibold">Detecciones</p>
                        <p className="text-2xl sm:text-3xl font-bold text-primary leading-none">
                          {analysisResult.detections?.length || 0}
                        </p>
                      </div>
                    </div>

                    {/* Detections Summary */}
                    {analysisResult.detections && analysisResult.detections.length > 0 && (
                      <div className="p-4 sm:p-5 rounded-xl bg-gradient-to-br from-card to-muted/20 border-2 border-border shadow-sm">
                        <h4 className="text-sm font-bold text-foreground mb-3 flex items-center gap-2">
                          <TrendingUp className="h-4 w-4 text-primary" />
                          Resumen de Detecciones
                        </h4>
                        <div className="space-y-2.5">
                          {(() => {
                            // Group detections by type and count them
                            const grouped = analysisResult.detections.reduce((acc, det) => {
                              const key = det.class_name || det.type || 'Desconocido'
                              acc[key] = (acc[key] || 0) + 1
                              return acc
                            }, {} as Record<string, number>)

                            return Object.entries(grouped).map(([type, count]) => (
                              <div key={type} className="flex justify-between items-center p-2.5 rounded-lg bg-muted/40 hover:bg-muted/60 transition-colors">
                                <span className="text-sm font-semibold text-foreground">{type}</span>
                                <span className="text-sm font-bold text-primary bg-primary/10 px-3 py-1 rounded-full">×{count}</span>
                              </div>
                            ))
                          })()}
                        </div>
                      </div>
                    )}

                    {/* Location Information */}
                    {analysisResult.location?.has_location && (
                      <div className="p-4 sm:p-5 rounded-xl bg-gradient-to-br from-card to-muted/20 border-2 border-border shadow-sm">
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
                          {analysisResult.location.altitude_meters && (
                            <div className="p-2.5 rounded-lg bg-muted/40">
                              <p className="text-xs text-muted-foreground font-semibold mb-1">Altitud</p>
                              <p className="text-sm text-foreground font-semibold">
                                {Math.round(analysisResult.location.altitude_meters)} metros
                              </p>
                            </div>
                          )}
                          {analysisResult.location.google_maps_url && (
                            <a
                              href={analysisResult.location.google_maps_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-2 text-sm font-semibold text-primary hover:text-primary/80 transition-colors mt-2 group"
                            >
                              Ver en Google Maps
                              <ExternalLink className="h-3.5 w-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                            </a>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Show message if no location data */}
                    {!analysisResult.location?.has_location && (
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

                    {/* Processing Information */}
                    {(analysisResult.analysis?.processing_time_ms || selectedImage) && (
                      <div className="p-4 sm:p-5 rounded-xl bg-gradient-to-br from-card to-muted/20 border-2 border-border shadow-sm">
                        <h4 className="text-sm font-bold text-foreground mb-3 flex items-center gap-2">
                          <Info className="h-4 w-4 text-primary" />
                          Información del Procesamiento
                        </h4>
                        <div className="space-y-2.5">
                          {analysisResult.analysis?.processing_time_ms && (
                            <div className="p-2.5 rounded-lg bg-muted/40">
                              <p className="text-xs text-muted-foreground font-semibold mb-1">Tiempo de Análisis</p>
                              <p className="text-sm text-foreground font-semibold">
                                {(analysisResult.analysis.processing_time_ms / 1000).toFixed(2)} segundos
                              </p>
                            </div>
                          )}
                          {selectedImage && (
                            <>
                              <div className="p-2.5 rounded-lg bg-muted/40">
                                <p className="text-xs text-muted-foreground font-semibold mb-1">Nombre del Archivo</p>
                                <p className="text-sm text-foreground break-all">
                                  {analysisResult.analysis?.image_filename || selectedImage.name}
                                </p>
                              </div>
                              <div className="p-2.5 rounded-lg bg-muted/40">
                                <p className="text-xs text-muted-foreground font-semibold mb-1">Tamaño del Archivo</p>
                                <p className="text-sm text-foreground font-semibold">
                                  {(selectedImage.size / (1024 * 1024)).toFixed(2)} MB
                                </p>
                              </div>
                            </>
                          )}
                          <div className="p-2.5 rounded-lg bg-muted/40">
                            <p className="text-xs text-muted-foreground font-semibold mb-1">Umbral de Confianza Usado</p>
                            <p className="text-sm text-foreground font-semibold">
                              {Math.round(confidenceThreshold * 100)}%
                            </p>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* CTA */}
                    <div className="p-5 rounded-xl bg-gradient-to-br from-primary/10 via-primary/5 to-transparent border-2 border-primary/30 shadow-sm">
                      <p className="text-sm text-foreground mb-3 leading-relaxed">
                        <span className="font-bold block mb-1">¿Guardar este análisis?</span>
                        Crea una cuenta para acceder a historial completo, mapas de riesgo y recomendaciones personalizadas.
                      </p>
                      <Link to={routes.public.register}>
                        <Button size="default" className="bg-primary hover:bg-primary/90 text-white w-full font-semibold shadow-sm hover:shadow transition-all">
                          Crear Cuenta Gratis
                        </Button>
                      </Link>
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
                {/* Upload Menu with Dropdown */}
                <div className="relative flex-1" ref={uploadMenuRef}>
                  <Button
                    onClick={handleAnalyzeAnother}
                    size="lg"
                    className="w-full bg-primary hover:bg-primary/90 text-white font-semibold shadow-sm hover:shadow transition-all"
                  >
                    <Upload className="mr-2 h-5 w-5" />
                    Analizar Otra Imagen
                  </Button>

                  {/* Dropdown Menu */}
                  {showUploadMenu && (
                    <div className="absolute bottom-full left-0 right-0 mb-3 bg-card border-2 border-border rounded-xl shadow-lg overflow-hidden z-50 animate-in slide-in-from-bottom-2 fade-in duration-200">
                      <button
                        onClick={() => handleSelectNewImage('camera')}
                        className="w-full px-4 py-3.5 flex items-center gap-3 hover:bg-muted/60 transition-all text-left group"
                      >
                        <div className="p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
                          <Camera className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-foreground">Tomar Foto</p>
                          <p className="text-xs text-muted-foreground">Usa la cámara de tu dispositivo</p>
                        </div>
                      </button>
                      <div className="h-px bg-border" />
                      <button
                        onClick={() => handleSelectNewImage('file')}
                        className="w-full px-4 py-3.5 flex items-center gap-3 hover:bg-muted/60 transition-all text-left group"
                      >
                        <div className="p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
                          <Upload className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-foreground">Subir Archivo</p>
                          <p className="text-xs text-muted-foreground">Selecciona desde tu galería</p>
                        </div>
                      </button>
                    </div>
                  )}
                </div>

                <Link to={routes.public.home} className="flex-1">
                  <Button
                    size="lg"
                    variant="outline"
                    className="w-full font-semibold border-2 hover:bg-muted/50 transition-all"
                  >
                    Volver al Inicio
                  </Button>
                </Link>
              </div>
            </div>
          )}

          {/* Hidden file inputs - available in all steps */}
          <input
            ref={fileInputRef}
            type="file"
            accept={fileConstraints.allowedTypes.join(',')}
            onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
            className="hidden"
          />

          <input
            ref={cameraInputRef}
            type="file"
            accept="image/*,.heic,.heif"
            capture="environment"
            onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
            className="hidden"
          />
        </div>
      </section>
      </div>
    </>
  )
}

export default ReportPage
