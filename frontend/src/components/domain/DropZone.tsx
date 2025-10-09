import React, { useCallback, useState } from 'react'
import { Upload, Image as ImageIcon, X, CheckCircle, AlertCircle } from 'lucide-react'
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
}

export const DropZone: React.FC<DropZoneProps> = ({
  onFilesSelected,
  accept = 'image/jpeg,image/png,image/jpg',
  maxSize = 10,
  maxFiles = 1,
  multiple = false,
  disabled = false,
  className,
}) => {
  const [isDragging, setIsDragging] = useState(false)
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [errors, setErrors] = useState<string[]>([])

  const validateFile = (file: File): string | null => {
    // Check file type
    const acceptedTypes = accept.split(',').map(t => t.trim())
    const fileType = file.type
    const isValidType = acceptedTypes.some(type => {
      if (type.endsWith('/*')) {
        return fileType.startsWith(type.replace('/*', ''))
      }
      return fileType === type
    })

    if (!isValidType) {
      return `${file.name}: Tipo de archivo no válido. Solo se permiten imágenes.`
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
      onFilesSelected(newSelectedFiles)
    }
  }, [selectedFiles, multiple, maxFiles, maxSize, accept, onFilesSelected])

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
    setSelectedFiles(newFiles)
    onFilesSelected(newFiles)
  }

  const handleClearAll = () => {
    setSelectedFiles([])
    setErrors([])
    onFilesSelected([])
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
          'relative border-2 border-dashed rounded-xl p-8 transition-all duration-200',
          isDragging && !disabled
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 bg-gray-50',
          disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:border-primary-400',
          className
        )}
      >
        <input
          type="file"
          accept={accept}
          multiple={multiple}
          onChange={handleFileInput}
          disabled={disabled}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          id="file-upload"
        />

        <div className="text-center">
          <div className={cn(
            'mx-auto w-16 h-16 rounded-full flex items-center justify-center mb-4',
            isDragging ? 'bg-primary-100' : 'bg-gray-200'
          )}>
            <Upload className={cn(
              'h-8 w-8',
              isDragging ? 'text-primary-600' : 'text-gray-500'
            )} />
          </div>

          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {isDragging ? 'Suelta la imagen aquí' : 'Arrastra tu imagen aquí'}
          </h3>

          <p className="text-sm text-gray-600 mb-4">
            o haz clic para seleccionar {multiple ? 'archivos' : 'un archivo'}
          </p>

          <div className="flex items-center justify-center gap-4 text-xs text-gray-500">
            <span>Formatos: JPG, PNG</span>
            <span>•</span>
            <span>Max: {maxSize}MB</span>
            {multiple && (
              <>
                <span>•</span>
                <span>Hasta {maxFiles} archivos</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Errors */}
      {errors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start gap-2">
            <AlertCircle className="h-5 w-5 text-red-600 shrink-0 mt-0.5" />
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-red-900 mb-1">
                Error de validación
              </h4>
              <ul className="text-sm text-red-800 space-y-1">
                {errors.map((error, index) => (
                  <li key={index}>• {error}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Selected Files */}
      {selectedFiles.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold text-gray-900">
              Archivos seleccionados ({selectedFiles.length})
            </h4>
            <Button
              onClick={handleClearAll}
              variant="ghost"
              size="sm"
              className="text-red-600 hover:text-red-700 hover:bg-red-50"
            >
              Limpiar todo
            </Button>
          </div>

          <div className="space-y-2">
            {selectedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center gap-3 bg-white border border-gray-200 rounded-lg p-3 hover:border-gray-300 transition-colors"
              >
                <div className="shrink-0 w-12 h-12 bg-primary-50 rounded-lg flex items-center justify-center">
                  <ImageIcon className="h-6 w-6 text-primary-600" />
                </div>

                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {file.name}
                  </p>
                  <p className="text-xs text-gray-600">
                    {formatFileSize(file.size)}
                  </p>
                </div>

                <CheckCircle className="h-5 w-5 text-green-600 shrink-0" />

                <Button
                  onClick={() => handleRemoveFile(index)}
                  variant="ghost"
                  size="sm"
                  className="shrink-0 text-gray-400 hover:text-red-600"
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
