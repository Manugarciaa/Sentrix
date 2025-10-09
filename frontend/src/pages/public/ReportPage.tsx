import React, { useState, useRef } from 'react'
import { Link } from 'react-router-dom'
import { Camera, Upload, CheckCircle, AlertCircle, X, Image as ImageIcon, MapPin, TrendingUp } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { routes, config, apiEndpoints, fileConstraints } from '@/lib/config'

interface AnalysisResult {
  id: string
  detections: Array<{
    type: string
    confidence: number
    bbox: [number, number, number, number]
  }>
  risk_level: string
  processed_image_url?: string
}

type UploadStep = 'upload' | 'preview' | 'analyzing' | 'results'

const ReportPage: React.FC = () => {
  const [step, setStep] = useState<UploadStep>('upload')
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)

  const fileInputRef = useRef<HTMLInputElement>(null)
  const cameraInputRef = useRef<HTMLInputElement>(null)

  const validateFile = (file: File): string | null => {
    if (!fileConstraints.allowedTypes.includes(file.type)) {
      return 'Formato de archivo no permitido. Use JPG, PNG, TIFF, HEIC, WebP o BMP.'
    }
    if (file.size > fileConstraints.maxSize) {
      return 'El archivo es demasiado grande. Máximo 50MB.'
    }
    return null
  }

  const handleFileSelect = (file: File) => {
    const validationError = validateFile(file)
    if (validationError) {
      setError(validationError)
      return
    }

    setSelectedImage(file)
    setError(null)

    const reader = new FileReader()
    reader.onload = (e) => {
      setImagePreview(e.target?.result as string)
      setStep('preview')
    }
    reader.readAsDataURL(file)
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

      const response = await fetch(`${config.api.baseUrl}${apiEndpoints.upload.image}`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Error al procesar la imagen')
      }

      const result = await response.json()
      setAnalysisResult(result)
      setStep('results')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al analizar la imagen')
      setStep('preview')
    }
  }

  const handleReset = () => {
    setStep('upload')
    setSelectedImage(null)
    setImagePreview(null)
    setAnalysisResult(null)
    setError(null)
  }

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel?.toLowerCase()) {
      case 'critico':
        return 'text-red-600 bg-red-50 border-red-200'
      case 'alto':
        return 'text-orange-600 bg-orange-50 border-orange-200'
      case 'medio':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'bajo':
        return 'text-green-600 bg-green-50 border-green-200'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      {/* Hero Section */}
      <section className="relative overflow-hidden min-h-screen flex items-center pt-28 pb-12 sm:pt-32 sm:pb-16">
        {/* Decorative background elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 right-0 w-96 h-96 bg-gradient-to-br from-primary-200/30 to-cyan-200/30 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-1/4 left-0 w-80 h-80 bg-gradient-to-br from-blue-200/20 to-primary-200/20 rounded-full blur-3xl"></div>
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-br from-cyan-100/10 to-blue-100/10 rounded-full blur-3xl"></div>
        </div>

        <div className="relative mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 w-full">
          <div className="text-center mb-8 sm:mb-10 md:mb-14">
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight text-gray-900 font-akira leading-tight mb-4 sm:mb-6 md:mb-8">
              Detector de<br />
              <span className="text-primary-600">Criaderos</span>
            </h1>

            <p className="mx-auto max-w-2xl text-base leading-relaxed text-gray-700 mb-6 sm:mb-8 md:mb-12 px-2 sm:px-4">
              Sube una imagen o toma una foto para analizar posibles criaderos del mosquito Aedes aegypti.
            </p>
          </div>

          {/* Info Banner */}
          <div className="mx-auto max-w-2xl mb-8 sm:mb-10 md:mb-12">
            <div className="bg-stone-50 border border-gray-200 rounded-xl p-4 shadow-sm">
              <div className="flex items-start gap-2 sm:gap-3">
                <AlertCircle className="h-4 w-4 sm:h-5 sm:w-5 text-gray-600 flex-shrink-0 mt-0.5" />
                <div className="text-left">
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                    Modo Demostración
                  </h3>
                  <p className="text-sm leading-normal text-gray-600">
                    Esta es una prueba del sistema. Los resultados no se guardarán.
                    Para colaborar con datos reales,{' '}
                    <Link to={routes.public.register} className="font-semibold text-primary-600 underline hover:text-primary-700">
                      crea una cuenta gratuita
                    </Link>.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Upload Section */}
          {step === 'upload' && (
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-primary-400/10 to-cyan-400/10 rounded-3xl blur-2xl group-hover:blur-3xl transition-all duration-500"></div>
              <div className="relative bg-white/90 backdrop-blur-sm rounded-2xl p-6 sm:p-8 border border-gray-200/50 shadow-xl">
                <div
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  className={`relative border-2 border-dashed rounded-2xl p-8 sm:p-12 text-center transition-all duration-500 overflow-hidden ${
                    isDragging
                      ? 'border-primary-500 bg-gradient-to-br from-primary-50 to-cyan-50 scale-[1.02]'
                      : 'border-gray-300 hover:border-primary-400 bg-gradient-to-br from-stone-50 to-white hover:shadow-inner'
                  }`}
                >
                  {isDragging && (
                    <div className="absolute inset-0 bg-gradient-to-br from-primary-100/50 to-cyan-100/50 animate-pulse"></div>
                  )}

                  <div className="relative z-10 mb-8">
                    <div className="mx-auto h-20 w-20 sm:h-24 sm:w-24 rounded-2xl bg-gradient-to-br from-primary-500 to-cyan-500 flex items-center justify-center mb-6 shadow-lg transform transition-transform group-hover:scale-110 duration-300">
                      <ImageIcon className="h-10 w-10 sm:h-12 sm:w-12 text-white" />
                    </div>
                    <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-3">
                      {isDragging ? '¡Suelta la imagen aquí!' : 'Sube o arrastra tu imagen'}
                    </h3>
                    <p className="text-base leading-relaxed text-gray-700 mb-2">
                      Formatos soportados: JPG, PNG, TIFF, HEIC, WebP, BMP
                    </p>
                    <p className="text-sm leading-normal text-gray-600">
                      Tamaño máximo: 50MB
                    </p>
                  </div>

                  <div className="relative z-10 flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center">
                    <Button
                      onClick={() => cameraInputRef.current?.click()}
                      size="lg"
                      className="group/btn bg-gradient-to-r from-primary-600 to-cyan-600 hover:from-primary-700 hover:to-cyan-700 text-white px-8 py-4 shadow-lg hover:shadow-xl transition-all"
                    >
                      <Camera className="mr-2 h-5 w-5 group-hover/btn:scale-110 transition-transform" />
                      Tomar Foto
                    </Button>

                    <Button
                      onClick={() => fileInputRef.current?.click()}
                      size="lg"
                      variant="outline"
                      className="group/btn border-2 border-primary-500 text-primary-700 hover:bg-primary-50 px-8 py-4 shadow-md hover:shadow-lg transition-all"
                    >
                      <Upload className="mr-2 h-5 w-5 group-hover/btn:scale-110 transition-transform" />
                      Subir Archivo
                    </Button>
                  </div>

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
                    accept="image/*"
                    capture="environment"
                    onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
                    className="hidden"
                  />
                </div>

                {error && (
                  <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-start gap-3 animate-in fade-in slide-in-from-top-2 duration-300">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 rounded-lg bg-red-100 flex items-center justify-center">
                        <AlertCircle className="h-4 w-4 text-red-600" />
                      </div>
                    </div>
                    <p className="text-sm text-red-800 leading-relaxed">{error}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Preview Section */}
          {step === 'preview' && imagePreview && (
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-primary-400/10 to-cyan-400/10 rounded-3xl blur-2xl"></div>
              <div className="relative bg-white/95 backdrop-blur-sm rounded-2xl p-6 sm:p-8 border-2 border-gray-200/50 shadow-2xl">
                <div className="flex justify-between items-center mb-6">
                  <div>
                    <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-1">Vista Previa</h3>
                    <p className="text-sm leading-normal text-gray-600">Verifica tu imagen antes de analizarla</p>
                  </div>
                  <button
                    onClick={handleReset}
                    className="p-2.5 hover:bg-red-50 rounded-xl transition-all duration-200 group/close border border-transparent hover:border-red-200"
                  >
                    <X className="h-5 w-5 text-gray-400 group-hover/close:text-red-600 transition-colors" />
                  </button>
                </div>

                <div className="mb-6 relative rounded-2xl overflow-hidden border-2 border-gray-200 bg-stone-50">
                  <img
                    src={imagePreview}
                    alt="Preview"
                    className="w-full h-auto max-h-[500px] object-contain"
                  />
                </div>

                <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
                  <Button
                    onClick={handleAnalyze}
                    size="lg"
                    className="flex-1 bg-gradient-to-r from-primary-600 to-cyan-600 hover:from-primary-700 hover:to-cyan-700 text-white shadow-lg hover:shadow-xl transform hover:scale-[1.02] transition-all"
                  >
                    <CheckCircle className="mr-2 h-5 w-5" />
                    Analizar Imagen
                  </Button>

                  <Button
                    onClick={handleReset}
                    size="lg"
                    variant="outline"
                    className="border-2 border-gray-300 text-gray-700 hover:bg-stone-100 hover:border-gray-400"
                  >
                    Cancelar
                  </Button>
                </div>

                {error && (
                  <div className="mt-6 p-4 bg-red-50 border-2 border-red-200 rounded-xl flex items-start gap-3">
                    <div className="w-8 h-8 rounded-lg bg-red-100 flex items-center justify-center flex-shrink-0">
                      <AlertCircle className="h-4 w-4 text-red-600" />
                    </div>
                    <p className="text-sm text-red-800 leading-relaxed">{error}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Analyzing Section */}
          {step === 'analyzing' && (
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-primary-400/20 to-cyan-400/20 rounded-3xl blur-3xl animate-pulse"></div>
              <div className="relative bg-white/95 backdrop-blur-sm rounded-2xl sm:rounded-3xl p-10 sm:p-14 border-2 border-primary-200/50 shadow-2xl">
                <div className="text-center">
                  <div className="relative mb-10">
                    <div className="absolute inset-0 bg-gradient-to-r from-primary-400 to-cyan-400 rounded-full blur-2xl opacity-30 animate-pulse"></div>
                    <div className="relative animate-spin h-20 w-20 sm:h-24 sm:w-24 border-4 border-primary-100 border-t-primary-600 border-r-cyan-600 rounded-full mx-auto shadow-xl"></div>
                  </div>
                  <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-4">
                    Analizando Imagen
                  </h3>
                  <p className="text-base leading-relaxed text-gray-700 mb-2 font-medium">
                    Nuestro modelo de IA está procesando tu imagen
                  </p>
                  <p className="text-sm leading-normal text-gray-600">
                    Detectando posibles criaderos del mosquito...
                  </p>

                  <div className="mt-8 flex justify-center gap-2">
                    <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-cyan-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Results Section */}
          {step === 'results' && analysisResult && (
            <div className="space-y-6">
              <div className="bg-white rounded-2xl p-6 sm:p-8 border border-gray-200 shadow-lg">
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <div className="inline-flex items-center gap-2 rounded-full bg-green-50 border border-green-200 px-4 py-1.5 text-sm leading-normal text-gray-600 font-medium mb-3">
                      <CheckCircle className="h-4 w-4" />
                      Análisis Completado
                    </div>
                    <h3 className="text-xl sm:text-2xl font-bold text-gray-900">Resultados</h3>
                  </div>
                  <button
                    onClick={handleReset}
                    className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                  >
                    <X className="h-5 w-5 text-gray-600" />
                  </button>
                </div>

                {/* Image with detections */}
                {(analysisResult.processed_image_url || imagePreview) && (
                  <div className="mb-6">
                    <img
                      src={analysisResult.processed_image_url || imagePreview || undefined}
                      alt="Analysis result"
                      className="w-full h-auto rounded-xl border border-gray-200 max-h-96 object-contain"
                    />
                  </div>
                )}

                {/* Stats Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
                  <div className="p-6 rounded-xl bg-gradient-to-br from-primary-50 to-white border border-gray-200 shadow-sm">
                    <div className="flex items-center gap-3 mb-2">
                      <TrendingUp className="h-5 w-5 text-primary-600" />
                      <h4 className="text-lg font-semibold text-gray-900">Detecciones</h4>
                    </div>
                    <p className="text-3xl font-bold text-primary-600">
                      {analysisResult.detections?.length || 0}
                    </p>
                  </div>

                  <div className={`p-6 rounded-xl border shadow-sm ${getRiskColor(analysisResult.risk_level)}`}>
                    <div className="flex items-center gap-3 mb-2">
                      <AlertCircle className="h-5 w-5" />
                      <h4 className="text-lg font-semibold text-gray-900">Nivel de Riesgo</h4>
                    </div>
                    <p className="text-3xl font-bold capitalize">
                      {analysisResult.risk_level || 'N/A'}
                    </p>
                  </div>

                  <div className="p-6 rounded-xl bg-gradient-to-br from-cyan-50 to-white border border-gray-200 shadow-sm">
                    <div className="flex items-center gap-3 mb-2">
                      <MapPin className="h-5 w-5 text-cyan-600" />
                      <h4 className="text-lg font-semibold text-gray-900">Tipos</h4>
                    </div>
                    <p className="text-sm leading-normal text-gray-600 font-medium">
                      {analysisResult.detections?.map(d => d.type).filter((v, i, a) => a.indexOf(v) === i).join(', ') || 'Ninguno'}
                    </p>
                  </div>
                </div>

                {/* Detections List */}
                {analysisResult.detections && analysisResult.detections.length > 0 && (
                  <div className="mb-6">
                    <h4 className="text-lg font-semibold text-gray-900 mb-3">Criaderos Detectados</h4>
                    <div className="space-y-2">
                      {analysisResult.detections.map((detection, idx) => (
                        <div key={idx} className="p-4 rounded-lg bg-stone-50 border border-gray-200">
                          <div className="flex justify-between items-center">
                            <span className="text-base leading-relaxed text-gray-700 font-medium">{detection.type}</span>
                            <span className="text-sm leading-normal text-gray-600 font-semibold">
                              {(detection.confidence * 100).toFixed(1)}% confianza
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* CTA */}
                <div className="p-6 rounded-xl bg-gradient-to-br from-primary-50 via-blue-50 to-cyan-50 border border-primary-200 shadow-sm">
                  <h4 className="text-lg font-semibold text-gray-900 mb-2">
                    ¿Quieres guardar este análisis?
                  </h4>
                  <p className="text-base leading-relaxed text-gray-700 mb-4">
                    Crea una cuenta para guardar tus análisis, ver historial y acceder a mapas de riesgo.
                  </p>
                  <Link to={routes.public.register}>
                    <Button className="bg-gradient-to-r from-primary-600 to-cyan-600 hover:from-primary-700 hover:to-cyan-700 text-white">
                      Crear Cuenta Gratis
                    </Button>
                  </Link>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
                <Button
                  onClick={handleReset}
                  size="lg"
                  className="flex-1 bg-gradient-to-r from-primary-600 to-cyan-600 hover:from-primary-700 hover:to-cyan-700 text-white"
                >
                  <Camera className="mr-2 h-5 w-5" />
                  Analizar Otra Imagen
                </Button>

                <Link to={routes.public.home} className="flex-1">
                  <Button
                    size="lg"
                    variant="outline"
                    className="w-full border-2 border-primary-500 text-primary-700 hover:bg-primary-50"
                  >
                    Volver al Inicio
                  </Button>
                </Link>
              </div>
            </div>
          )}
        </div>
      </section>
    </div>
  )
}

export default ReportPage
