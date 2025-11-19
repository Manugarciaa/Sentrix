import { useMutation, useQueryClient } from '@tanstack/react-query'
import { analysisService } from '@/services/analysisService'
import { queryKeys } from '@/lib/queryKeys'
import { toast } from '@/lib/toast'
import { config, apiEndpoints } from '@/lib/config'
import type {
  AnalysisUploadData,
  BatchUploadData,
  AnalysisResponse,
  BatchAnalysisResponse
} from '@/services/analysisService'

// Types for upload progress tracking
export interface UploadProgress {
  uploadId: string
  fileName: string
  progress: number
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'failed'
  error?: string
}

export interface BatchUploadProgress {
  batchId: string
  totalFiles: number
  completedFiles: number
  failedFiles: number
  currentFile?: string
  overallProgress: number
  items: UploadProgress[]
}

// Single upload mutation hook
export const useUploadAnalysis = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: AnalysisUploadData & { onProgress?: (progress: number) => void }) => {
      const { onProgress, ...uploadData } = data

      // Check if user is authenticated
      const token = localStorage.getItem(config.auth.tokenKey)
      if (!token) {
        throw new Error('Debes iniciar sesión para subir imágenes.')
      }

      // Create a custom fetch with progress tracking
      const formData = new FormData()
      formData.append('file', uploadData.file)

      if (uploadData.confidence_threshold !== undefined) {
        formData.append('confidence_threshold', uploadData.confidence_threshold.toString())
      }
      if (uploadData.include_gps !== undefined) {
        formData.append('include_gps', uploadData.include_gps.toString())
      }
      if (uploadData.latitude !== undefined) {
        formData.append('latitude', uploadData.latitude.toString())
      }
      if (uploadData.longitude !== undefined) {
        formData.append('longitude', uploadData.longitude.toString())
      }

      // Use XMLHttpRequest for progress tracking
      return new Promise<AnalysisResponse>((resolve, reject) => {
        const xhr = new XMLHttpRequest()
        
        // Track upload progress
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable && onProgress) {
            const progress = Math.round((event.loaded / event.total) * 100)
            onProgress(progress)
          }
        })

        xhr.addEventListener('load', () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            try {
              const response = JSON.parse(xhr.responseText)
              resolve(response)
            } catch (error) {
              reject(new Error('Invalid response format'))
            }
          } else if (xhr.status === 401) {
            // Unauthorized - token expired or invalid
            reject(new Error('Sesión expirada. Por favor, inicia sesión nuevamente.'))
            // Clear tokens
            localStorage.removeItem(config.auth.tokenKey)
            localStorage.removeItem(config.auth.refreshTokenKey)
            // Redirect to login
            setTimeout(() => {
              window.location.href = '/auth/login?redirect=' + encodeURIComponent(window.location.pathname)
            }, 1500)
          } else if (xhr.status === 403) {
            reject(new Error('No tienes permisos para realizar esta acción.'))
          } else if (xhr.status === 413) {
            reject(new Error('El archivo es demasiado grande. Máximo 50MB.'))
          } else {
            try {
              const errorResponse = JSON.parse(xhr.responseText)
              const errorMessage = errorResponse.error?.message || errorResponse.message || errorResponse.detail
              reject(new Error(errorMessage || `Error ${xhr.status}: ${xhr.statusText}`))
            } catch {
              reject(new Error(`Error ${xhr.status}: ${xhr.statusText}`))
            }
          }
        })

        xhr.addEventListener('error', () => {
          reject(new Error('Error de conexión. Verifica tu conexión a internet y que el servidor esté disponible.'))
        })

        xhr.addEventListener('timeout', () => {
          reject(new Error('Upload timeout'))
        })

        // Set timeout to 5 minutes for large files
        xhr.timeout = 5 * 60 * 1000

        // Open and send request
        xhr.open('POST', `${config.api.baseUrl}${apiEndpoints.analyses.create}`)

        // Add auth header if available
        const token = localStorage.getItem(config.auth.tokenKey)
        if (token) {
          xhr.setRequestHeader('Authorization', `Bearer ${token}`)
        }

        xhr.send(formData)
      })
    },
    onSuccess: (data) => {
      // Invalidate and refetch analyses list
      queryClient.invalidateQueries({ queryKey: queryKeys.analyses.lists() })
      
      // Invalidate dashboard data
      queryClient.invalidateQueries({ queryKey: queryKeys.reports.dashboard() })
      
      // Show success message
      toast.success('Análisis completado exitosamente')
    },
    onError: (error: Error) => {
      console.error('Upload error:', error)
      toast.error(error.message || 'Error al subir la imagen')
    },
    // Disable automatic retries for uploads
    retry: false,
  })
}

// Batch upload mutation hook
export const useBatchUploadAnalyses = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: BatchUploadData & { 
      onProgress?: (progress: BatchUploadProgress) => void 
      onItemProgress?: (itemId: string, progress: UploadProgress) => void
    }) => {
      const { onProgress, onItemProgress, ...uploadData } = data
      const batchId = `batch-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      
      const batchProgress: BatchUploadProgress = {
        batchId,
        totalFiles: uploadData.files.length,
        completedFiles: 0,
        failedFiles: 0,
        overallProgress: 0,
        items: uploadData.files.map((file, index) => ({
          uploadId: `${batchId}-item-${index}`,
          fileName: file.name,
          progress: 0,
          status: 'pending',
        })),
      }

      // Process files sequentially to avoid overwhelming the server
      const results: (AnalysisResponse | { error: string; fileName: string })[] = []
      
      for (let i = 0; i < uploadData.files.length; i++) {
        const file = uploadData.files[i]
        const itemProgress = batchProgress.items[i]
        
        try {
          // Update current file being processed
          batchProgress.currentFile = file.name
          itemProgress.status = 'uploading'
          
          if (onProgress) onProgress({ ...batchProgress })
          if (onItemProgress) onItemProgress(itemProgress.uploadId, { ...itemProgress })

          // Upload single file
          const singleUploadData: AnalysisUploadData = {
            file,
            ...uploadData.options,
          }

          const result = await new Promise<AnalysisResponse>((resolve, reject) => {
            const formData = new FormData()
            formData.append('file', file)

            if (uploadData.options?.confidence_threshold !== undefined) {
              formData.append('confidence_threshold', uploadData.options.confidence_threshold.toString())
            }
            if (uploadData.options?.include_gps !== undefined) {
              formData.append('include_gps', uploadData.options.include_gps.toString())
            }
            if (uploadData.options?.latitude !== undefined) {
              formData.append('latitude', uploadData.options.latitude.toString())
            }
            if (uploadData.options?.longitude !== undefined) {
              formData.append('longitude', uploadData.options.longitude.toString())
            }

            const xhr = new XMLHttpRequest()
            
            // Track individual file progress
            xhr.upload.addEventListener('progress', (event) => {
              if (event.lengthComputable) {
                const progress = Math.round((event.loaded / event.total) * 100)
                itemProgress.progress = progress
                
                if (onItemProgress) {
                  onItemProgress(itemProgress.uploadId, { ...itemProgress })
                }
              }
            })

            xhr.addEventListener('load', () => {
              if (xhr.status >= 200 && xhr.status < 300) {
                try {
                  const response = JSON.parse(xhr.responseText)
                  resolve(response)
                } catch (error) {
                  reject(new Error('Invalid response format'))
                }
              } else if (xhr.status === 401) {
                reject(new Error('Sesión expirada.'))
              } else if (xhr.status === 403) {
                reject(new Error('Sin permisos.'))
              } else if (xhr.status === 413) {
                reject(new Error('Archivo muy grande.'))
              } else {
                try {
                  const errorResponse = JSON.parse(xhr.responseText)
                  const errorMessage = errorResponse.error?.message || errorResponse.message || errorResponse.detail
                  reject(new Error(errorMessage || `Error ${xhr.status}`))
                } catch {
                  reject(new Error(`Error ${xhr.status}: ${xhr.statusText}`))
                }
              }
            })

            xhr.addEventListener('error', () => {
              reject(new Error('Network error occurred'))
            })

            xhr.addEventListener('timeout', () => {
              reject(new Error('Upload timeout'))
            })

            // Set timeout to 5 minutes per file
            xhr.timeout = 5 * 60 * 1000

            xhr.open('POST', `${config.api.baseUrl}${apiEndpoints.analyses.create}`)

            // Add auth header if available
            const token = localStorage.getItem(config.auth.tokenKey)
            if (token) {
              xhr.setRequestHeader('Authorization', `Bearer ${token}`)
            }

            xhr.send(formData)
          })

          // Success
          itemProgress.status = 'completed'
          itemProgress.progress = 100
          batchProgress.completedFiles++
          results.push(result)

        } catch (error) {
          // Error
          itemProgress.status = 'failed'
          itemProgress.error = error instanceof Error ? error.message : 'Unknown error'
          batchProgress.failedFiles++
          results.push({
            error: itemProgress.error,
            fileName: file.name,
          })
        }

        // Update overall progress
        batchProgress.overallProgress = Math.round(
          ((batchProgress.completedFiles + batchProgress.failedFiles) / batchProgress.totalFiles) * 100
        )

        if (onProgress) onProgress({ ...batchProgress })
        if (onItemProgress) onItemProgress(itemProgress.uploadId, { ...itemProgress })
      }

      // Return batch results
      const successfulResults = results.filter((r): r is AnalysisResponse => 'analysis' in r)
      const failedResults = results.filter((r): r is { error: string; fileName: string } => 'error' in r)

      return {
        results: successfulResults,
        total_processed: uploadData.files.length,
        successful: successfulResults.length,
        failed: failedResults.length,
        errors: failedResults.map(r => `${r.fileName}: ${r.error}`),
        batchProgress,
      }
    },
    onSuccess: (data) => {
      // Invalidate and refetch analyses list
      queryClient.invalidateQueries({ queryKey: queryKeys.analyses.lists() })
      
      // Invalidate dashboard data
      queryClient.invalidateQueries({ queryKey: queryKeys.reports.dashboard() })
      
      // Show success message
      if (data.successful > 0) {
        toast.success(`${data.successful} análisis completados exitosamente`)
      }
      
      if (data.failed > 0) {
        toast.error(`${data.failed} análisis fallaron`)
      }
    },
    onError: (error: Error) => {
      console.error('Batch upload error:', error)
      toast.error(error.message || 'Error en el procesamiento por lotes')
    },
    // Disable automatic retries for batch uploads
    retry: false,
  })
}

// Hook for cancelling uploads
export const useUploadCancellation = () => {
  const abortControllers = new Map<string, AbortController>()

  const createCancellableUpload = (uploadId: string) => {
    const controller = new AbortController()
    abortControllers.set(uploadId, controller)
    return controller
  }

  const cancelUpload = (uploadId: string) => {
    const controller = abortControllers.get(uploadId)
    if (controller) {
      controller.abort()
      abortControllers.delete(uploadId)
    }
  }

  const cancelAllUploads = () => {
    abortControllers.forEach((controller) => {
      controller.abort()
    })
    abortControllers.clear()
  }

  return {
    createCancellableUpload,
    cancelUpload,
    cancelAllUploads,
  }
}

// Hook for upload queue management
export const useUploadQueue = () => {
  const queryClient = useQueryClient()

  const retryFailedUpload = useMutation({
    mutationFn: async (data: { file: File; options?: any }) => {
      return analysisService.uploadAnalysis({
        file: data.file,
        ...data.options,
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.analyses.lists() })
      toast.success('Reintento exitoso')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error en el reintento')
    },
  })

  return {
    retryFailedUpload,
  }
}