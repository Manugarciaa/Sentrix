import { useMutation, useQueryClient } from '@tanstack/react-query'
import { analysisService } from '@/services/analysisService'
import { queryKeys } from '@/lib/queryKeys'
import { toast } from 'sonner'
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
          } else {
            try {
              const errorResponse = JSON.parse(xhr.responseText)
              reject(new Error(errorResponse.message || `HTTP ${xhr.status}`))
            } catch {
              reject(new Error(`HTTP ${xhr.status}: ${xhr.statusText}`))
            }
          }
        })

        xhr.addEventListener('error', () => {
          reject(new Error('Network error occurred'))
        })

        xhr.addEventListener('timeout', () => {
          reject(new Error('Upload timeout'))
        })

        // Set timeout to 5 minutes for large files
        xhr.timeout = 5 * 60 * 1000

        // Open and send request
        xhr.open('POST', `${import.meta.env.VITE_API_BASE_URL}/api/v1/analyses`)
        
        // Add auth header if available
        const token = localStorage.getItem('access_token')
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
              } else {
                try {
                  const errorResponse = JSON.parse(xhr.responseText)
                  reject(new Error(errorResponse.message || `HTTP ${xhr.status}`))
                } catch {
                  reject(new Error(`HTTP ${xhr.status}: ${xhr.statusText}`))
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

            xhr.open('POST', `${import.meta.env.VITE_API_BASE_URL}/api/v1/analyses`)
            
            // Add auth header if available
            const token = localStorage.getItem('access_token')
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