import React, { useCallback, useState, useRef } from 'react'
import { Upload, Image as ImageIcon, X, CheckCircle, AlertCircle, Camera } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'

export interface DropZoneProps {
  onFilesSelected: (files: File[]) => void
  accept?: string
  maxSize?: number // in MB
  maxFiles?: number
  multiple?: boolean
  disabled?: boolean
  className?: string
  showCamera?: boolean // New prop to enable camera option
  showPreview?: boolean // New prop to show image preview
}

export const DropZone: React.FC<DropZoneProps> = ({
  onFilesSelected,
  accept = 'image/jpeg,image/png,image/jpg,image/tiff,image/heic,image/heif,image/webp,image/bmp',
  maxSize = 10,
  maxFiles = 1,
  multiple = false,
  disabled = false,
  className,
  showCamera = true,
  showPreview = true,
}) => {
  const [isDragging, setIsDragging] = useState(false)
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [errors, setErrors] = useState<string[]>([])
  const [previewUrls, setPreviewUrls] = useState<string[]>([])

  const fileInputRef = useRef<HTMLInputElement>(null)
  const cameraInputRef = useRef<HTMLInputElement>(null)

  const validateFile = (file: File): string | null => {
    // Check file type - also check by extension for formats like HEIC
    const acceptedTypes = accept.split(',').map(t => t.trim())
    const fileType = file.type
    const fileName = file.name.toLowerCase()
    const fileExtension = fileName.substring(fileName.lastIndexOf('.'))

    // Allowed extensions based on accept types
    const extensionMap: Record<string, string[]> = {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/jpg': ['.jpg', '.jpeg'],
      'image/tiff': ['.tiff', '.tif'],
      'image/heic': ['.heic'],
      'image/heif': ['.heif'],
      'image/webp': ['.webp'],
      'image/bmp': ['.bmp']
    }

    // Check by MIME type
    let isValidType = acceptedTypes.some(type => {
      if (type.endsWith('/*')) {
        return fileType.startsWith(type.replace('/*', ''))
      }
      return fileType === type
    })

    // If MIME type doesn't match, check by extension (important for HEIC/HEIF)
    if (!isValidType) {
      isValidType = acceptedTypes.some(type => {
        const extensions = extensionMap[type] || []
        return extensions.includes(fileExtension)
      })
    }

    // Also accept if file type is empty but extension is valid (common for HEIC on some browsers)
    if (!isValidType && !fileType) {
      const allExtensions = Object.values(extensionMap).flat()
      isValidType = allExtensions.includes(fileExtension)
    }

    if (!isValidType) {
      return `${file.name}: Tipo de archivo no válido. Formatos permitidos: JPG, PNG, TIFF, HEIC, HEIF, WebP, BMP.`
    }

    // Check file size
    const fileSizeMB = file.size / (1024 * 1024)
    if (fileSizeMB > maxSize) {
      return `${file.name}: Tamaño máximo ${maxSize}MB. El archivo tiene ${fileSizeMB.toFixed(2)}MB.`
    }

    return null
  }

  const handleFiles = useCallback((files: FileList | null) => {
    if (!files || files.length === 0) return

    const fileArray = Array.from(files)
    const newErrors: string[] = []
    const validFiles: File[] = []

    // Validate each file
    for (const file of fileArray) {
      const error = validateFile(file)
      if (error) {
        newErrors.push(error)
      } else {
        validFiles.push(file)
      }
    }

    // Check max files
    const totalFiles = selectedFiles.length + validFiles.length
    if (totalFiles > maxFiles) {
      newErrors.push(`Máximo ${maxFiles} archivo${maxFiles > 1 ? 's' : ''} permitido${maxFiles > 1 ? 's' : ''}.`)
      setErrors(newErrors)
      return
    }

    setErrors(newErrors)

    if (validFiles.length > 0) {
      const newSelectedFiles = multiple
        ? [...selectedFiles, ...validFiles]
        : validFiles

      setSelectedFiles(newSelectedFiles)

      // Generate preview URLs if showPreview is enabled
      if (showPreview) {
        const newPreviews: string[] = []
        validFiles.forEach(file => {
          const reader = new FileReader()
          reader.onload = (e) => {
            if (e.target?.result) {
              newPreviews.push(e.target.result as string)
              if (newPreviews.length === validFiles.length) {
                setPreviewUrls(multiple ? [...previewUrls, ...newPreviews] : newPreviews)
              }
            }
          }
          reader.readAsDataURL(file)
        })
      }

      onFilesSelected(newSelectedFiles)
    }
  }, [selectedFiles, multiple, maxFiles, maxSize, accept, onFilesSelected, showPreview, previewUrls])

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (!disabled) {
      setIsDragging(true)
    }
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    if (disabled) return

    const { files } = e.dataTransfer
    handleFiles(files)
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files)
  }

  const handleRemoveFile = (index: number) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index)
    const newPreviews = previewUrls.filter((_, i) => i !== index)
    setSelectedFiles(newFiles)
    setPreviewUrls(newPreviews)
    onFilesSelected(newFiles)
  }

  const handleClearAll = () => {
    setSelectedFiles([])
    setPreviewUrls([])
    setErrors([])
    onFilesSelected([])
  }

  const handleCameraClick = () => {
    cameraInputRef.current?.click()
  }

  const handleFileClick = () => {
    fileInputRef.current?.click()
  }

  const formatFileSize = (bytes: number) => {
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  }

  return (
    <div className={cn('space-y-4', className)}>
      {/* Drop Zone */}
      <div
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        className={cn(
          'border-2 border-dashed rounded-2xl p-8 transition-all duration-300 group',
          isDragging && !disabled
            ? 'border-primary bg-primary/5 shadow-lg scale-[1.02]'
            : 'border-border bg-muted/30 hover:bg-muted/50',
          disabled && 'opacity-50 cursor-not-allowed',
          className
        )}
      >
        <div className="text-center">
          <div className={cn(
            'mx-auto w-16 h-16 rounded-2xl flex items-center justify-center mb-4 transition-all duration-300',
            isDragging ? 'bg-primary/20 scale-110 shadow-lg' : 'bg-card group-hover:bg-primary/10 group-hover:scale-105',
            'border-2',
            isDragging ? 'border-primary' : 'border-border group-hover:border-primary/50'
          )}>
            <ImageIcon className={cn(
              'h-8 w-8 transition-all duration-300',
              isDragging ? 'text-primary animate-bounce' : 'text-muted-foreground group-hover:text-primary'
            )} />
          </div>

          <h3 className="text-lg font-semibold text-foreground mb-2 transition-colors">
            {isDragging ? '¡Suelta la imagen aquí!' : 'Sube o arrastra tu imagen'}
          </h3>

          <p className="text-sm text-muted-foreground mb-1">
            Formatos soportados: JPG, PNG, TIFF, HEIC, WebP, BMP
          </p>
          <p className="text-xs text-muted-foreground mb-6">
            Tamaño máximo: {maxSize}MB
          </p>

          {/* Camera and Upload Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            {showCamera && (
              <Button
                onClick={handleCameraClick}
                disabled={disabled}
                size="lg"
                type="button"
                className="pointer-events-auto"
              >
                <Camera className="mr-2 h-5 w-5" />
                Tomar Foto
              </Button>
            )}

            <Button
              onClick={handleFileClick}
              disabled={disabled}
              size="lg"
              variant={showCamera ? "outline" : "default"}
              type="button"
              className="pointer-events-auto"
            >
              <Upload className="mr-2 h-5 w-5" />
              Subir Archivo
            </Button>
          </div>
        </div>

        {/* Hidden inputs */}
        <input
          ref={fileInputRef}
          type="file"
          accept={accept}
          multiple={multiple}
          onChange={handleFileInput}
          disabled={disabled}
          className="hidden"
          aria-label="Subir archivos"
        />

        {showCamera && (
          <input
            ref={cameraInputRef}
            type="file"
            accept="image/*,.heic,.heif"
            capture="environment"
            onChange={handleFileInput}
            disabled={disabled}
            className="hidden"
            aria-label="Tomar foto"
          />
        )}
      </div>

      {/* Errors */}
      {errors.length > 0 && (
        <div className="bg-red-50 dark:bg-red-950/20 border-2 border-red-200 dark:border-red-800/50 rounded-xl p-4 shadow-sm">
          <div className="flex items-start gap-3">
            <div className="shrink-0 w-10 h-10 rounded-lg bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
              <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
            </div>
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-red-900 dark:text-red-300 mb-2">
                Error de validación
              </h4>
              <ul className="text-sm text-red-800 dark:text-red-400/90 space-y-1.5">
                {errors.map((error, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-red-400 dark:text-red-500 mt-1">•</span>
                    <span className="flex-1">{error}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Image Preview */}
      {showPreview && previewUrls.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-semibold text-foreground px-1">
            Vista Previa
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {previewUrls.map((url, index) => (
              <div key={index} className="relative rounded-lg overflow-hidden border-2 border-border bg-muted/30 group">
                <img
                  src={url}
                  alt={`Preview ${index + 1}`}
                  className="w-full h-48 object-contain"
                />
                <Button
                  onClick={() => handleRemoveFile(index)}
                  variant="ghost"
                  size="sm"
                  className="absolute top-2 right-2 h-8 w-8 p-0 bg-background/80 backdrop-blur-sm hover:bg-red-50 dark:hover:bg-red-950/50 text-muted-foreground hover:text-red-600 dark:hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                  aria-label={`Eliminar imagen ${index + 1}`}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Selected Files */}
      {selectedFiles.length > 0 && !showPreview && (
        <div className="space-y-4">
          <div className="flex items-center justify-between px-1">
            <h4 className="text-sm font-semibold text-foreground">
              Archivos seleccionados ({selectedFiles.length})
            </h4>
            <Button
              onClick={handleClearAll}
              variant="ghost"
              size="sm"
              className="text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-950/20"
            >
              Limpiar todo
            </Button>
          </div>

          <div className="space-y-2.5">
            {selectedFiles.map((file, index) => (
              <div
                key={index}
                className="group flex items-center gap-4 bg-card border-2 border-border rounded-xl p-4 hover:border-primary/40 hover:shadow-md transition-all duration-300"
              >
                <div className="shrink-0 w-12 h-12 bg-primary/10 dark:bg-primary/20 rounded-xl flex items-center justify-center border border-primary/20 dark:border-primary/30">
                  <ImageIcon className="h-6 w-6 text-primary" />
                </div>

                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-foreground truncate mb-1">
                    {file.name}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {formatFileSize(file.size)}
                  </p>
                </div>

                <div className="shrink-0 w-8 h-8 rounded-lg bg-green-100 dark:bg-green-950/30 flex items-center justify-center border border-green-200 dark:border-green-800/50">
                  <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
                </div>

                <Button
                  onClick={() => handleRemoveFile(index)}
                  variant="ghost"
                  size="sm"
                  className="shrink-0 h-8 w-8 p-0 text-muted-foreground hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/20 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                  aria-label={`Eliminar ${file.name}`}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default DropZone
