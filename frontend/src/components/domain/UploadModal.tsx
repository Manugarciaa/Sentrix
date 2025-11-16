import React, { useState, useRef, useCallback } from 'react'
import { createPortal } from 'react-dom'
import { useNavigate } from 'react-router-dom'
import { Camera, Upload as UploadIcon, CheckCircle, X, Image as ImageIcon, MapPin, SlidersHorizontal, AlertCircle } from 'lucide-react'
import heic2any from 'heic2any'
import exifr from 'exifr'
import { Button } from '@/components/ui/Button'
import { Slider } from '@/components/ui/Slider'
import { routes, fileConstraints, config, apiEndpoints } from '@/lib/config'
import { showToast } from '@/lib/toast'
import LocationPicker from '@/components/domain/LocationPicker'

type Step = 'upload' | 'detecting' | 'preview' | 'confirming'

interface UploadModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess?: () => void
}

const UploadModal: React.FC<UploadModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const navigate = useNavigate()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const cameraInputRef = useRef<HTMLInputElement>(null)

  const [step, setStep] = useState<Step>('upload')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [processedImageUrl, setProcessedImageUrl] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  // Configuration
  const [confidenceThreshold, setConfidenceThreshold] = useState(50) // 50% (mismo que demo y app)

  // Detection results (temporary, before confirming)
  const [detectionCount, setDetectionCount] = useState<number>(0)
  const [detectionResult, setDetectionResult] = useState<'detected' | 'not-detected' | null>(null)

  // GPS detection
  const [detectedGPS, setDetectedGPS] = useState<{ lat: number; lng: number } | null>(null)
  const [isDetectingGPS, setIsDetectingGPS] = useState(false)

  // Manual GPS
  const [showLocationPicker, setShowLocationPicker] = useState(false)
  const [manualLat, setManualLat] = useState<number | null>(null)
  const [manualLng, setManualLng] = useState<number | null>(null)

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

  const detectGPS = useCallback(async (file: File) => {
    setIsDetectingGPS(true)
    try {
      // Configure exifr to handle all image formats including HEIC
      const exifData = await exifr.parse(file, {
        gps: true,
        tiff: true,
        ifd0: true,
        ifd1: true,
        exif: true,
        pick: ['latitude', 'longitude', 'GPSLatitude', 'GPSLongitude', 'GPSLatitudeRef', 'GPSLongitudeRef']
      })

      console.log('EXIF data:', exifData)

      if (exifData && exifData.latitude !== undefined && exifData.longitude !== undefined) {
        let lat = exifData.latitude
        let lng = exifData.longitude

        // Apply direction signs manually if needed
        // exifr might not apply signs correctly in some cases
        if (exifData.GPSLatitudeRef === 'S' && lat > 0) {
          lat = -lat
        }
        if (exifData.GPSLongitudeRef === 'W' && lng > 0) {
          lng = -lng
        }

        setDetectedGPS({
          lat: lat,
          lng: lng
        })
        console.log(`✅ GPS detectado: ${lat}, ${lng} (Ref: ${exifData.GPSLatitudeRef}, ${exifData.GPSLongitudeRef})`)
        showToast.success('GPS detectado', `Ubicación encontrada en la imagen`)
      } else {
        console.log('❌ No GPS data in EXIF:', exifData)
        setDetectedGPS(null)
      }
    } catch (error) {
      console.error('Error detecting GPS:', error)
      setDetectedGPS(null)
    } finally {
      setIsDetectingGPS(false)
    }
  }, [])

  const detectWithAI = useCallback(async (file: File) => {
    setStep('detecting')
    setDetectionResult(null)
    setProcessedImageUrl(null)
    setDetectionCount(0)

    showToast.info('Analizando imagen', 'Detectando posibles criaderos con IA...')

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('confidence_threshold', (confidenceThreshold / 100).toString())

      const response = await fetch(`${config.api.baseUrl}${apiEndpoints.upload.image}`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Error al procesar la imagen')
      }

      const data = await response.json()

      // Determinar si se detectaron criaderos
      const count = data.detections?.length || 0
      setDetectionCount(count)
      const detected = count > 0
      setDetectionResult(detected ? 'detected' : 'not-detected')

      // Guardar imagen procesada si existe
      if (data.processed_image_url) {
        setProcessedImageUrl(data.processed_image_url)
      }

      // Mover a preview
      setStep('preview')

      // Toast con resultado
      if (detected) {
        showToast.success(
          'Detección completada',
          `Se identificaron ${count} posible${count > 1 ? 's' : ''} criadero${count > 1 ? 's' : ''}.`
        )
      } else {
        showToast.info(
          'Detección completada',
          'No se detectaron posibles criaderos en esta imagen.'
        )
      }
    } catch (err) {
      console.error('Detection error:', err)
      showToast.error('Error al detectar', 'No se pudo procesar la imagen. Intenta de nuevo.')
      setStep('upload')
      setSelectedFile(null)
      setPreviewUrl(null)
    }
  }, [confidenceThreshold])

  const processFile = useCallback(async (file: File) => {
    const validationError = validateFile(file)
    if (validationError) {
      showToast.error('Archivo inválido', validationError)
      return
    }

    setIsProcessing(true)
    setSelectedFile(null)
    setPreviewUrl(null)
    setDetectedGPS(null)
    setManualLat(null)
    setManualLng(null)

    const isHEIC = file.name.toLowerCase().match(/\.(heic|heif)$/)

    if (isHEIC) {
      try {
        showToast.info('Convirtiendo HEIC', 'Procesando archivo...')

        // ⚠️ IMPORTANTE: Detectar GPS del archivo HEIC ORIGINAL antes de convertir
        // La conversión heic2any elimina los metadatos EXIF
        detectGPS(file)

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
          setIsProcessing(false)
          // Auto-detect with AI
          detectWithAI(convertedFile)
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

      // Detect GPS from original file
      detectGPS(file)

      const reader = new FileReader()
      reader.onload = (e) => {
        setPreviewUrl(e.target?.result as string)
        setIsProcessing(false)
        // Auto-detect with AI
        detectWithAI(file)
      }
      reader.readAsDataURL(file)
    }

    if (fileInputRef.current) fileInputRef.current.value = ''
    if (cameraInputRef.current) cameraInputRef.current.value = ''
  }, [validateFile, detectGPS, detectWithAI])

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

  const handleConfirmAnalysis = useCallback(async () => {
    if (!selectedFile) return

    setStep('confirming')
    setUploadProgress(0)

    showToast.info('Guardando análisis', 'Creando registro con las detecciones encontradas...')

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('confidence_threshold', (confidenceThreshold / 100).toString())

      // Always try to extract GPS from image (backend will handle it)
      formData.append('include_gps', 'true')

      // If user manually provided coordinates, send them as well
      const finalLat = manualLat !== null ? manualLat : (detectedGPS?.lat ?? null)
      const finalLng = manualLng !== null ? manualLng : (detectedGPS?.lng ?? null)

      if (finalLat !== null && finalLng !== null) {
        formData.append('latitude', finalLat.toString())
        formData.append('longitude', finalLng.toString())
      }

      const token = localStorage.getItem(config.auth.tokenKey)
      if (!token) {
        showToast.error('No autenticado', 'Inicia sesión para continuar')
        setTimeout(() => navigate('/auth/login?redirect=/app/analysis'), 1500)
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
        setTimeout(() => navigate('/auth/login?redirect=/app/analysis'), 1500)
        return
      }

      if (!createResponse.ok) {
        const errorData = await createResponse.json().catch(() => ({}))
        throw new Error(errorData.message || errorData.detail || `Error ${createResponse.status}`)
      }

      const createData = await createResponse.json()
      const analysisId = createData.analysis_id

      setUploadProgress(100)

      showToast.success('Análisis guardado', 'Procesando imagen con IA...')

      // Close modal and trigger refresh
      if (onSuccess) onSuccess()
      handleReset()
      onClose()

      // Navigate to detail with longer delay to allow backend processing
      // Especialmente importante para archivos HEIC que toman más tiempo
      setTimeout(() => {
        navigate(`${routes.app.analysis}/${analysisId}`)
      }, 3000)  // Aumentado de 500ms a 3000ms (3 segundos)

    } catch (err) {
      console.error('[UPLOAD] Save analysis error:', err)
      setStep('preview')
      const errorMessage = err instanceof Error ? err.message : 'No se pudo guardar el análisis'
      showToast.error('Error al guardar', errorMessage)
    }
  }, [selectedFile, confidenceThreshold, manualLat, manualLng, detectedGPS, navigate, onSuccess, onClose])

  const handleReset = useCallback(() => {
    setStep('upload')
    setSelectedFile(null)
    setPreviewUrl(null)
    setProcessedImageUrl(null)
    setUploadProgress(0)
    setDetectionResult(null)
    setDetectionCount(0)
    setDetectedGPS(null)
    setIsDetectingGPS(false)
    setManualLat(null)
    setManualLng(null)
  }, [])

  const handleClose = () => {
    handleReset()
    onClose()
  }

  if (!isOpen) return null

  const modalContent = (
    <div
      className="fixed top-0 left-0 right-0 bottom-0 z-[100] flex items-center justify-center bg-black/30 backdrop-blur-sm"
      style={{ position: 'fixed', inset: 0 }}
    >
      <div className="bg-card border border-border rounded-2xl shadow-2xl w-full max-w-4xl max-h-[95vh] overflow-hidden flex flex-col m-4">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-card">
          <div>
            <h2 className="text-2xl font-bold text-foreground">Nuevo Análisis</h2>
            <p className="text-sm text-muted-foreground mt-0.5">
              Detecta criaderos del mosquito Aedes aegypti con IA
            </p>
          </div>
          <button
            onClick={handleClose}
            className="p-2 hover:bg-muted rounded-lg transition-colors"
          >
            <X className="h-5 w-5 text-muted-foreground" />
          </button>
        </div>

        {/* Content - Scrollable */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Upload Step */}
          {step === 'upload' && !isProcessing && (
            <>
              {/* Configuration */}
              <div className="mb-6">
                <div className="flex items-center gap-2 mb-4">
                  <SlidersHorizontal className="h-4 w-4 text-primary" />
                  <h3 className="text-base font-semibold text-foreground">Configuración del Análisis</h3>
                </div>
                <div className="bg-muted/30 border border-border rounded-xl p-5">
                  {/* Umbral de Confianza */}
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
                </div>
              </div>

              {/* Drop Zone */}
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <UploadIcon className="h-4 w-4 text-primary" />
                  <h3 className="text-base font-semibold text-foreground">Cargar Imagen</h3>
                </div>
                <div
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  className={`border-2 border-dashed rounded-xl p-10 text-center transition-all ${
                    isDragging
                      ? 'border-primary bg-primary/10 scale-[1.01]'
                      : 'border-border hover:border-primary/50 hover:bg-muted/20'
                  }`}
                >
                  <div className="mb-6">
                    <div className="mx-auto h-16 w-16 rounded-2xl bg-gradient-to-br from-primary/20 to-primary/10 flex items-center justify-center mb-4">
                      <ImageIcon className="h-8 w-8 text-primary" />
                    </div>
                    <h3 className="text-lg font-semibold text-foreground mb-2">
                      {isDragging ? 'Suelta la imagen aquí' : 'Arrastra tu imagen o selecciona'}
                    </h3>
                    <div className="space-y-1 mb-1">
                      <p className="text-sm text-muted-foreground">
                        Formatos soportados: JPG, PNG, TIFF, HEIC, WebP, BMP
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Tamaño máximo: 50MB
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-3 justify-center max-w-md mx-auto">
                    <Button
                      onClick={() => cameraInputRef.current?.click()}
                      size="lg"
                      className="flex-1 gap-2"
                    >
                      <Camera className="h-5 w-5" />
                      Tomar Foto
                    </Button>

                    <Button
                      onClick={() => fileInputRef.current?.click()}
                      size="lg"
                      variant="outline"
                      className="flex-1 gap-2"
                    >
                      <UploadIcon className="h-5 w-5" />
                      Seleccionar Archivo
                    </Button>
                  </div>
                </div>
              </div>
            </>
          )}

          {/* Processing */}
          {isProcessing && (
            <div className="text-center py-16">
              <div className="mb-6">
                <div className="animate-spin h-16 w-16 border-4 border-muted border-t-primary rounded-full mx-auto"></div>
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-2">
                Procesando Imagen
              </h3>
              <p className="text-sm text-muted-foreground">
                Preparando tu imagen...
              </p>
            </div>
          )}

          {/* Preview */}
          {step === 'preview' && previewUrl && (
            <div className="space-y-6">
              {/* Image Preview with Detections */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <ImageIcon className="h-4 w-4 text-primary" />
                    <h3 className="text-base font-semibold text-foreground">Resultado de Detección</h3>
                  </div>
                  {detectionResult && (
                    <div className="flex items-center gap-2 px-3 py-1 rounded-full" style={{
                      backgroundColor: detectionResult === 'detected' ? 'hsl(var(--status-warning-bg) / 0.2)' : 'hsl(var(--status-success-bg) / 0.2)',
                      borderColor: detectionResult === 'detected' ? 'hsl(var(--status-warning-border))' : 'hsl(var(--status-success-border))',
                      border: '1px solid'
                    }}>
                      <span className="text-xs font-semibold" style={{
                        color: detectionResult === 'detected' ? 'hsl(var(--status-warning-text))' : 'hsl(var(--status-success-text))'
                      }}>
                        {detectionResult === 'detected' ? `${detectionCount} detección${detectionCount !== 1 ? 'es' : ''}` : 'Sin detecciones'}
                      </span>
                    </div>
                  )}
                </div>
                <div className="rounded-xl overflow-hidden border border-border bg-muted/20">
                  <img
                    src={processedImageUrl || previewUrl}
                    alt="Preview con detecciones"
                    className="w-full h-auto max-h-[350px] object-contain"
                  />
                </div>
                {detectionResult === 'detected' && (
                  <div className="flex flex-wrap items-center justify-center gap-3 mt-3 px-3 py-2 bg-muted/30 rounded-lg">
                    <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Leyenda:</span>
                    <div className="flex items-center gap-1.5">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: 'rgb(255, 140, 0)' }} />
                      <span className="text-xs text-foreground">Basura</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: 'rgb(0, 100, 255)' }} />
                      <span className="text-xs text-foreground">Charcos/Agua</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: 'rgb(0, 200, 0)' }} />
                      <span className="text-xs text-foreground">Huecos</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: 'rgb(255, 0, 0)' }} />
                      <span className="text-xs text-foreground">Calles</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Location Section */}
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <MapPin className="h-4 w-4 text-primary" />
                  <h3 className="text-base font-semibold text-foreground">Ubicación GPS</h3>
                  <span className="text-xs text-muted-foreground">(Opcional)</span>
                </div>

                {isDetectingGPS ? (
                  <div className="p-4 rounded-xl border border-border bg-muted/20">
                    <div className="flex items-center gap-3">
                      <div className="animate-spin h-5 w-5 border-2 border-muted border-t-primary rounded-full"></div>
                      <p className="text-sm text-muted-foreground">Detectando GPS de la imagen...</p>
                    </div>
                  </div>
                ) : manualLat !== null && manualLng !== null ? (
                  <div className="p-4 rounded-xl border" style={{
                    backgroundColor: 'hsl(var(--status-success-bg) / 0.1)',
                    borderColor: 'hsl(var(--status-success-border))'
                  }}>
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex gap-3 flex-1">
                        <CheckCircle className="h-5 w-5 flex-shrink-0" style={{ color: 'hsl(var(--status-success-text))' }} />
                        <div className="flex-1">
                          <p className="text-sm font-semibold mb-1" style={{ color: 'hsl(var(--status-success-text))' }}>
                            Ubicación agregada manualmente
                          </p>
                          <p className="text-xs text-foreground font-mono">
                            {manualLat.toFixed(6)}, {manualLng.toFixed(6)}
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={handleRemoveManualLocation}
                        className="p-1.5 hover:bg-muted rounded transition-colors"
                      >
                        <X className="h-4 w-4 text-muted-foreground" />
                      </button>
                    </div>
                  </div>
                ) : detectedGPS !== null ? (
                  <div className="p-4 rounded-xl border" style={{
                    backgroundColor: 'hsl(var(--status-success-bg) / 0.1)',
                    borderColor: 'hsl(var(--status-success-border))'
                  }}>
                    <div className="flex gap-3">
                      <CheckCircle className="h-5 w-5 flex-shrink-0" style={{ color: 'hsl(var(--status-success-text))' }} />
                      <div className="flex-1">
                        <p className="text-sm font-semibold mb-1" style={{ color: 'hsl(var(--status-success-text))' }}>
                          GPS detectado en la imagen
                        </p>
                        <p className="text-xs text-foreground font-mono">
                          {detectedGPS.lat.toFixed(6)}, {detectedGPS.lng.toFixed(6)}
                        </p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="p-4 rounded-xl border border-border bg-muted/20">
                    <div className="flex gap-3 mb-3">
                      <AlertCircle className="h-5 w-5 flex-shrink-0 text-muted-foreground" />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-foreground mb-1">
                          No se detectó GPS en la imagen
                        </p>
                        <p className="text-xs text-muted-foreground">
                          Puedes agregar la ubicación manualmente usando el mapa o continuar sin GPS
                        </p>
                      </div>
                    </div>
                    <Button
                      onClick={() => setShowLocationPicker(true)}
                      variant="outline"
                      size="sm"
                      className="w-full gap-2"
                    >
                      <MapPin className="h-4 w-4" />
                      Agregar Ubicación en el Mapa
                    </Button>
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 pt-2">
                <Button
                  onClick={handleConfirmAnalysis}
                  size="lg"
                  className="flex-1 gap-2"
                >
                  <CheckCircle className="h-5 w-5" />
                  Confirmar y Guardar Análisis
                </Button>

                <Button
                  onClick={handleReset}
                  size="lg"
                  variant="outline"
                  className="gap-2"
                >
                  <X className="h-4 w-4" />
                  Cancelar
                </Button>
              </div>
            </div>
          )}

          {/* Detecting with AI */}
          {step === 'detecting' && (
            <div className="text-center py-16">
              <div className="mb-6">
                <div className="relative mx-auto h-16 w-16">
                  <div className="absolute inset-0 animate-spin h-16 w-16 border-4 border-muted border-t-primary rounded-full"></div>
                  <div className="absolute inset-2 rounded-full bg-primary/10 flex items-center justify-center">
                    <ImageIcon className="h-6 w-6 text-primary" />
                  </div>
                </div>
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-2">
                Detectando con IA
              </h3>
              <p className="text-sm text-muted-foreground">
                Analizando imagen para detectar posibles criaderos...
              </p>
            </div>
          )}

          {/* Confirming and Saving */}
          {step === 'confirming' && (
            <div className="text-center py-16">
              <div className="mb-6">
                <div className="relative mx-auto h-16 w-16">
                  <div className="absolute inset-0 animate-spin h-16 w-16 border-4 border-muted border-t-primary rounded-full"></div>
                  <div className="absolute inset-2 rounded-full bg-primary/10 flex items-center justify-center">
                    <CheckCircle className="h-6 w-6 text-primary" />
                  </div>
                </div>
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-2">
                Guardando Análisis
              </h3>
              <p className="text-sm text-muted-foreground mb-6">
                Creando registro con las detecciones encontradas...
              </p>
              {uploadProgress > 0 && (
                <div className="max-w-sm mx-auto">
                  <div className="w-full bg-muted rounded-full h-2.5 overflow-hidden">
                    <div
                      className="bg-primary h-full rounded-full transition-all duration-300"
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                  <p className="text-sm font-medium text-foreground mt-3">{uploadProgress}%</p>
                </div>
              )}
            </div>
          )}
        </div>

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

        {/* Location Picker Modal */}
        {showLocationPicker && (
          <LocationPicker
            onLocationSelect={handleLocationSelect}
            onClose={() => setShowLocationPicker(false)}
            initialLat={manualLat ?? detectedGPS?.lat ?? undefined}
            initialLng={manualLng ?? detectedGPS?.lng ?? undefined}
          />
        )}
      </div>
    </div>
  )

  return createPortal(modalContent, document.body)
}

export default UploadModal
