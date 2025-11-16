import React, { useState, useCallback, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { Upload, Loader2, UserPlus, Maximize2, X } from 'lucide-react'
import heic2any from 'heic2any'
import { Button } from '@/components/ui/Button'
import { routes, config, apiEndpoints, fileConstraints } from '@/lib/config'
import { showToast } from '@/lib/toast'

interface AnalysisResult {
  detections: Array<{
    type?: string
    class_name?: string
    confidence: number
  }>
  processed_image_url?: string
}

const DemoSection: React.FC = () => {
  const [isDragging, setIsDragging] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState<'detected' | 'not-detected' | null>(null)
  const [previewImage, setPreviewImage] = useState<string | null>(null)
  const [processedImage, setProcessedImage] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [detectionCount, setDetectionCount] = useState<number>(0)
  const [isImageModalOpen, setIsImageModalOpen] = useState(false)
  const [zoomLevel, setZoomLevel] = useState(1)
  const [panPosition, setPanPosition] = useState({ x: 0, y: 0 })
  const [isDraggingImage, setIsDraggingImage] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const scrollPositionRef = useRef(0)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const modalRef = useRef<HTMLDivElement>(null)

  const handleCloseImageModal = useCallback(() => {
    setIsImageModalOpen(false)
    setZoomLevel(1)
    setPanPosition({ x: 0, y: 0 })
  }, [])

  // Handle ESC key to close modal and prevent body scroll when modal is open
  useEffect(() => {
    const handleEscKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isImageModalOpen) {
        handleCloseImageModal()
      }
    }

    const preventScroll = (e: WheelEvent | TouchEvent) => {
      e.preventDefault()
    }

    if (isImageModalOpen) {
      // Save current scroll position
      scrollPositionRef.current = window.scrollY

      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden'
      document.body.style.position = 'fixed'
      document.body.style.top = `-${scrollPositionRef.current}px`
      document.body.style.width = '100%'

      // Prevent wheel and touch events on the document
      document.addEventListener('wheel', preventScroll, { passive: false })
      document.addEventListener('touchmove', preventScroll, { passive: false })
      document.addEventListener('keydown', handleEscKey)

      return () => {
        document.removeEventListener('wheel', preventScroll, { passive: false } as EventListenerOptions)
        document.removeEventListener('touchmove', preventScroll, { passive: false } as EventListenerOptions)
        document.removeEventListener('keydown', handleEscKey)

        // Restore scroll position when modal closes
        const scrollY = scrollPositionRef.current
        document.body.style.overflow = ''
        document.body.style.position = ''
        document.body.style.top = ''
        document.body.style.width = ''
        window.scrollTo(0, scrollY)
      }
    }
  }, [isImageModalOpen, handleCloseImageModal])

  // Handle wheel event on modal with passive: false
  useEffect(() => {
    const modalElement = modalRef.current
    if (!modalElement || !isImageModalOpen) return

    const handleWheelEvent = (e: WheelEvent) => {
      e.preventDefault()
      e.stopPropagation()

      const delta = e.deltaY * -0.001
      setZoomLevel(prevZoom => {
        const newZoom = prevZoom + delta
        return Math.min(Math.max(0.5, newZoom), 5) // Min 0.5x, Max 5x
      })
    }

    modalElement.addEventListener('wheel', handleWheelEvent, { passive: false })

    return () => {
      modalElement.removeEventListener('wheel', handleWheelEvent, { passive: false } as EventListenerOptions)
    }
  }, [isImageModalOpen])

  const validateFile = (file: File): string | null => {
    let isValidType = fileConstraints.allowedTypes.includes(file.type)

    if (!isValidType || !file.type) {
      const fileName = file.name.toLowerCase()
      const fileExtension = fileName.substring(fileName.lastIndexOf('.'))
      isValidType = fileConstraints.allowedExtensions.includes(fileExtension)
    }

    if (!isValidType) {
      return 'Formato no permitido. Use JPG, PNG, HEIC o WebP.'
    }
    if (file.size > 10 * 1024 * 1024) { // 10MB para demo
      return 'El archivo es muy grande. Máximo 10MB.'
    }
    return null
  }

  // Análisis real con el backend
  const analyzeImage = async (file: File) => {
    setIsAnalyzing(true)
    setResult(null)
    setProcessedImage(null)
    setDetectionCount(0)

    showToast.info('Analizando imagen', 'Detectando posibles criaderos con IA...')

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(`${config.api.baseUrl}${apiEndpoints.upload.image}`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Error al procesar la imagen')
      }

      const data: AnalysisResult = await response.json()

      // Determinar si se detectaron criaderos
      const count = data.detections?.length || 0
      setDetectionCount(count)
      const detected = count > 0
      setResult(detected ? 'detected' : 'not-detected')

      // Guardar imagen procesada si existe
      if (data.processed_image_url) {
        setProcessedImage(data.processed_image_url)
      }

      // Toast con resultado
      if (detected) {
        showToast.warning(
          'Posibles criaderos detectados',
          `Se identificaron ${count} posible${count > 1 ? 's' : ''} criadero${count > 1 ? 's' : ''}. Revisá la imagen y considerá crear un reporte oficial si lo confirmás.`,
          { duration: 15000, position: 'top-center' }
        )
      } else {
        showToast.success(
          'Análisis completado',
          'No se detectaron posibles criaderos en esta imagen.',
          { duration: 6000, position: 'top-center' }
        )
      }

      setIsAnalyzing(false)
    } catch (err) {
      console.error('Analysis error:', err)
      showToast.error('Error al analizar', 'No se pudo procesar la imagen. Intenta de nuevo.')
      setIsAnalyzing(false)
      setResult(null)
    }
  }

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const file = e.dataTransfer.files[0]
    if (file) {
      handleImageFile(file)
    }
  }, [])

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleImageFile(file)
    }
  }

  const handleImageFile = async (file: File) => {
    // Validar archivo
    const validationError = validateFile(file)
    if (validationError) {
      showToast.error('Archivo no válido', validationError)
      return
    }

    setResult(null)
    setProcessedImage(null)

    // Verificar si es HEIC
    const isHEIC = file.name.toLowerCase().match(/\.(heic|heif)$/)

    if (isHEIC) {
      showToast.info('Convirtiendo imagen', 'Procesando archivo HEIC...')
      try {
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
          setPreviewImage(e.target?.result as string)
          // Iniciar análisis automáticamente
          analyzeImage(convertedFile)
        }
        reader.readAsDataURL(blob)
      } catch (err) {
        console.error('Error converting HEIC:', err)
        showToast.error('Error de conversión', 'No se pudo convertir el archivo HEIC. Intenta con JPG o PNG.')
      }
    } else {
      setSelectedFile(file)
      const reader = new FileReader()
      reader.onload = (e) => {
        setPreviewImage(e.target?.result as string)
        // Iniciar análisis automáticamente
        analyzeImage(file)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleLoadAnother = () => {
    // Abrir selector de archivos directamente
    fileInputRef.current?.click()
  }

  const handleOpenImageModal = () => {
    if (!isAnalyzing) {
      // Reset zoom and pan BEFORE opening modal
      setZoomLevel(1)
      setPanPosition({ x: 0, y: 0 })
      setIsDraggingImage(false)
      // Open modal in the next tick to ensure state is reset
      setTimeout(() => {
        setIsImageModalOpen(true)
      }, 0)
    }
  }

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (zoomLevel > 1) {
      setIsDraggingImage(true)
      setDragStart({
        x: e.clientX - panPosition.x,
        y: e.clientY - panPosition.y
      })
    }
  }, [zoomLevel, panPosition])

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (isDraggingImage && zoomLevel > 1) {
      setPanPosition({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      })
    }
  }, [isDraggingImage, zoomLevel, dragStart])

  const handleMouseUp = useCallback(() => {
    setIsDraggingImage(false)
  }, [])

  return (
    <section className="bg-background min-h-screen flex items-center py-16 sm:py-20">
      <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 w-full">
        {/* Header */}
        <div className="text-center mb-12">
          <h2 id="demo" className="scroll-mt-24 text-3xl sm:text-4xl font-bold text-foreground mb-4">
            Probá el detector de IA
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Probá cómo Sentrix detecta posibles criaderos en una imagen.
            <br />
            <span className="text-sm">Las fotos no se guardan ni se asocian a tu cuenta.</span>
          </p>
        </div>

        {/* Demo Container */}
        <div className="bg-card border border-border rounded-2xl p-6 sm:p-8 shadow-lg">
          {!previewImage ? (
            /* Upload Area */
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`relative border-2 border-dashed rounded-xl transition-all duration-300 ${
                isDragging
                  ? 'border-primary bg-primary/5 scale-[1.02]'
                  : 'border-border hover:border-primary/50 hover:bg-muted/20'
              }`}
            >
              <label
                htmlFor="demo-image-upload"
                className="flex flex-col items-center justify-center py-12 px-6 sm:py-14 sm:px-8 md:py-16 cursor-pointer"
              >
                <Upload className={`h-12 w-12 sm:h-14 sm:w-14 md:h-16 md:w-16 mb-4 transition-colors ${isDragging ? 'text-primary' : 'text-muted-foreground'}`} />
                <p className="text-base sm:text-lg font-semibold text-foreground mb-2">
                  {isDragging ? 'Soltá la imagen aquí' : 'Arrastrá una imagen o hacé click'}
                </p>
                <p className="text-sm text-muted-foreground">
                  Formatos: JPG, PNG, HEIC (máx. 10MB)
                </p>
              </label>
              <input
                id="demo-image-upload"
                type="file"
                accept="image/*"
                onChange={handleFileInput}
                className="hidden"
              />
            </div>
          ) : (
            /* Analysis Area */
            <div className="space-y-4">
              {/* Preview Image */}
              <div
                className={`relative rounded-xl overflow-hidden bg-muted/30 ${!isAnalyzing ? 'cursor-pointer group' : ''}`}
                onClick={handleOpenImageModal}
              >
                <img
                  src={processedImage || previewImage}
                  alt="Preview"
                  className="w-full h-auto max-h-64 sm:max-h-80 md:max-h-96 object-contain transition-transform duration-200"
                  loading="lazy"
                  decoding="async"
                />

                {/* Hover overlay with expand icon */}
                {!isAnalyzing && (
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-200 flex items-center justify-center">
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 bg-white/90 dark:bg-gray-800/90 rounded-full p-3 shadow-lg">
                      <Maximize2 className="h-5 w-5 sm:h-6 sm:w-6 text-gray-800 dark:text-white" />
                    </div>
                  </div>
                )}

                {isAnalyzing && (
                  <div className="absolute inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center">
                    <div className="bg-card/95 rounded-xl p-4 sm:p-5 md:p-6 text-center">
                      <Loader2 className="h-10 w-10 sm:h-12 sm:w-12 text-primary animate-spin mx-auto mb-3" />
                      <p className="text-foreground font-semibold">Analizando imagen...</p>
                      <p className="text-sm text-muted-foreground mt-1">Detectando posibles criaderos con IA</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Color Legend - Only show when detection is complete */}
              {result === 'detected' && !isAnalyzing && (
                <div className="flex flex-wrap items-center justify-center gap-4 px-3 py-2 sm:px-4 sm:py-3 bg-muted/30 rounded-lg">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    Leyenda:
                  </span>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: 'rgb(255, 140, 0)' }} />
                    <span className="text-xs text-foreground">Basura</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: 'rgb(0, 100, 255)' }} />
                    <span className="text-xs text-foreground">Charcos/Agua</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: 'rgb(0, 200, 0)' }} />
                    <span className="text-xs text-foreground">Huecos</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: 'rgb(255, 0, 0)' }} />
                    <span className="text-xs text-foreground">Calles</span>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Button
                  onClick={handleLoadAnother}
                  variant="outline"
                  className="border-2 border-border hover:bg-muted hover:border-primary/50 dark:hover:border-primary/60 transition-all duration-300"
                  disabled={isAnalyzing}
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Probar otra imagen
                </Button>

                {result === 'detected' && (
                  <Link to={routes.public.register}>
                    <Button className="bg-primary hover:bg-primary/90 dark:hover:bg-primary/80 text-white transition-all duration-300 w-full sm:w-auto">
                      <UserPlus className="h-4 w-4 mr-2" />
                      Crear cuenta y reportar
                    </Button>
                  </Link>
                )}
              </div>

              {/* Hidden file input for re-upload */}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileInput}
                className="hidden"
              />
            </div>
          )}

          {/* Privacy Note */}
          <div className="mt-6 pt-6 border-t border-border">
            <p className="text-xs text-muted-foreground text-center">
              🔒 <strong>Modo Demo:</strong> Las imágenes se analizan con IA real pero no se guardan en tu historial.
              Para guardar reportes y acceder al mapa completo, creá una cuenta.
            </p>
          </div>
        </div>

        {/* Simple Image Modal with Zoom */}
        {isImageModalOpen && (
          <div
            ref={modalRef}
            className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4"
            onClick={handleCloseImageModal}
          >
            {/* Close button */}
            <button
              onClick={handleCloseImageModal}
              className="absolute top-4 right-4 z-10 bg-white/10 hover:bg-white/20 backdrop-blur-sm rounded-full p-2 transition-colors"
              aria-label="Cerrar"
            >
              <X className="h-6 w-6 text-white" />
            </button>

            {/* Zoom indicator */}
            <div className="absolute top-4 left-4 z-10 bg-white/10 backdrop-blur-sm rounded-lg px-3 py-2">
              <p className="text-sm text-white font-medium">
                {Math.round(zoomLevel * 100)}%
              </p>
            </div>

            {/* Color Legend - Fixed overlay in modal */}
            {result === 'detected' && (
              <div className="absolute bottom-20 left-4 z-10 bg-white/10 backdrop-blur-sm rounded-lg px-3 py-2">
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1.5">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: 'rgb(255, 140, 0)' }} />
                    <span className="text-xs text-white">Basura</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: 'rgb(0, 100, 255)' }} />
                    <span className="text-xs text-white">Charcos/Agua</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: 'rgb(0, 200, 0)' }} />
                    <span className="text-xs text-white">Huecos</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: 'rgb(255, 0, 0)' }} />
                    <span className="text-xs text-white">Calles</span>
                  </div>
                </div>
              </div>
            )}

            {/* Image Container */}
            <div
              className="relative overflow-hidden"
              style={{
                width: '100%',
                height: '100%',
                cursor: zoomLevel > 1 ? (isDraggingImage ? 'grabbing' : 'grab') : 'default'
              }}
              onClick={(e) => e.stopPropagation()}
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
            >
              <img
                src={processedImage || previewImage || ''}
                alt="Vista ampliada"
                className="absolute top-1/2 left-1/2 transition-transform duration-100"
                loading="lazy"
                decoding="async"
                style={{
                  transform: `translate(-50%, -50%) translate(${panPosition.x}px, ${panPosition.y}px) scale(${zoomLevel})`,
                  transformOrigin: 'center center',
                  maxWidth: '90vw',
                  maxHeight: '90vh',
                  width: 'auto',
                  height: 'auto'
                }}
                draggable={false}
              />
            </div>

            {/* Hint text */}
            <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-white/10 backdrop-blur-sm rounded-lg px-4 py-2">
              <p className="text-xs text-white/80 text-center">
                Usá la rueda del mouse para zoom • Arrastrá para mover • ESC o click fuera para cerrar
              </p>
            </div>
          </div>
        )}
      </div>
    </section>
  )
}

export default DemoSection
