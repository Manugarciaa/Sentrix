import React, { useEffect, useState, useCallback } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useAppStore } from '@/store/app'

/**
 * Network status interface
 */
export interface NetworkStatus {
  isOnline: boolean
  isSlowConnection: boolean
  effectiveType?: string
  downlink?: number
  rtt?: number
  saveData?: boolean
}

/**
 * Network recovery options
 */
export interface NetworkRecoveryOptions {
  enableNotifications?: boolean
  enableAutoRetry?: boolean
  retryDelay?: number
  maxRetries?: number
  onOnline?: () => void
  onOffline?: () => void
  onSlowConnection?: () => void
}

/**
 * Hook for monitoring network status and handling recovery
 */
export const useNetworkStatus = (): NetworkStatus => {
  const [networkStatus, setNetworkStatus] = useState<NetworkStatus>({
    isOnline: navigator.onLine,
    isSlowConnection: false,
  })

  useEffect(() => {
    const updateNetworkStatus = () => {
      const connection = (navigator as any).connection || 
                        (navigator as any).mozConnection || 
                        (navigator as any).webkitConnection

      const status: NetworkStatus = {
        isOnline: navigator.onLine,
        isSlowConnection: false,
      }

      if (connection) {
        status.effectiveType = connection.effectiveType
        status.downlink = connection.downlink
        status.rtt = connection.rtt
        status.saveData = connection.saveData

        // Consider connection slow if:
        // - Effective type is 'slow-2g' or '2g'
        // - Downlink is less than 1 Mbps
        // - RTT is greater than 1000ms
        status.isSlowConnection = 
          connection.effectiveType === 'slow-2g' ||
          connection.effectiveType === '2g' ||
          (connection.downlink && connection.downlink < 1) ||
          (connection.rtt && connection.rtt > 1000)
      }

      setNetworkStatus(status)
    }

    // Initial status
    updateNetworkStatus()

    // Listen for network changes
    const handleOnline = () => {
      updateNetworkStatus()
    }

    const handleOffline = () => {
      updateNetworkStatus()
    }

    const handleConnectionChange = () => {
      updateNetworkStatus()
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    // Listen for connection changes if supported
    const connection = (navigator as any).connection || 
                      (navigator as any).mozConnection || 
                      (navigator as any).webkitConnection

    if (connection) {
      connection.addEventListener('change', handleConnectionChange)
    }

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
      
      if (connection) {
        connection.removeEventListener('change', handleConnectionChange)
      }
    }
  }, [])

  return networkStatus
}

/**
 * Hook for network recovery with React Query integration
 */
export const useNetworkRecovery = (options: NetworkRecoveryOptions = {}) => {
  const queryClient = useQueryClient()
  const networkStatus = useNetworkStatus()
  const [wasOffline, setWasOffline] = useState(false)
  const [retryCount, setRetryCount] = useState(0)

  const {
    enableNotifications = true,
    enableAutoRetry = true,
    retryDelay = 2000,
    maxRetries = 3,
    onOnline,
    onOffline,
    onSlowConnection,
  } = options

  // Handle online/offline transitions
  useEffect(() => {
    if (networkStatus.isOnline && wasOffline) {
      // Network recovered
      console.log('🌐 Network recovered - resuming operations')
      
      if (enableNotifications) {
        useAppStore.getState().addNotification({
          type: 'success',
          title: 'Conexión restaurada',
          message: 'La conexión a internet se ha restaurado.',
          duration: 3000,
        })
      }

      if (enableAutoRetry) {
        // Resume paused mutations
        queryClient.resumePausedMutations()
        
        // Invalidate and refetch all queries
        queryClient.invalidateQueries()
        
        // Reset retry count
        setRetryCount(0)
      }

      // Call custom online handler
      if (onOnline) {
        onOnline()
      }

      setWasOffline(false)
    } else if (!networkStatus.isOnline && !wasOffline) {
      // Network lost
      console.log('🚫 Network lost - pausing operations')
      
      if (enableNotifications) {
        useAppStore.getState().addNotification({
          type: 'warning',
          title: 'Sin conexión',
          message: 'Se ha perdido la conexión a internet. Las operaciones se reanudarán automáticamente.',
          duration: 5000,
          persistent: true,
        })
      }

      // Call custom offline handler
      if (onOffline) {
        onOffline()
      }

      setWasOffline(true)
    }
  }, [networkStatus.isOnline, wasOffline, enableNotifications, enableAutoRetry, onOnline, onOffline, queryClient])

  // Handle slow connection
  useEffect(() => {
    if (networkStatus.isSlowConnection && networkStatus.isOnline) {
      console.log('🐌 Slow connection detected')
      
      if (enableNotifications) {
        useAppStore.getState().addNotification({
          type: 'info',
          title: 'Conexión lenta',
          message: 'Se ha detectado una conexión lenta. Las operaciones pueden tardar más tiempo.',
          duration: 4000,
        })
      }

      // Call custom slow connection handler
      if (onSlowConnection) {
        onSlowConnection()
      }
    }
  }, [networkStatus.isSlowConnection, networkStatus.isOnline, enableNotifications, onSlowConnection])

  // Retry failed operations
  const retryFailedOperations = useCallback(async () => {
    if (!networkStatus.isOnline || retryCount >= maxRetries) {
      return false
    }

    try {
      console.log(`🔄 Retrying failed operations (attempt ${retryCount + 1}/${maxRetries})`)
      
      // Wait for retry delay
      await new Promise(resolve => setTimeout(resolve, retryDelay))
      
      // Resume paused mutations
      await queryClient.resumePausedMutations()
      
      // Refetch failed queries
      await queryClient.refetchQueries({
        type: 'all',
        stale: true,
      })

      setRetryCount(prev => prev + 1)
      return true
    } catch (error) {
      console.error('[ERROR] Retry failed:', error)
      setRetryCount(prev => prev + 1)
      return false
    }
  }, [networkStatus.isOnline, retryCount, maxRetries, retryDelay, queryClient])

  // Force retry function
  const forceRetry = useCallback(() => {
    setRetryCount(0)
    return retryFailedOperations()
  }, [retryFailedOperations])

  return {
    networkStatus,
    isOnline: networkStatus.isOnline,
    isSlowConnection: networkStatus.isSlowConnection,
    wasOffline,
    retryCount,
    maxRetries,
    canRetry: retryCount < maxRetries,
    retryFailedOperations,
    forceRetry,
  }
}

/**
 * Error boundary component for network failures
 */
export class NetworkErrorBoundary extends React.Component<
  {
    children: React.ReactNode
    fallback?: React.ComponentType<{ error: Error; retry: () => void }>
    onError?: (error: Error, errorInfo: React.ErrorInfo) => void
  },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: any) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error) {
    // Check if this is a network-related error
    const isNetworkError = 
      error.message?.includes('Failed to fetch') ||
      error.message?.includes('Network') ||
      error.message?.includes('ERR_NETWORK') ||
      error.name === 'NetworkError'

    if (isNetworkError) {
      return { hasError: true, error }
    }

    // Let other error boundaries handle non-network errors
    throw error
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('🚨 Network Error Boundary caught an error:', error, errorInfo)
    
    // Call custom error handler
    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }

    // Show network error notification
    useAppStore.getState().addNotification({
      type: 'error',
      title: 'Error de conexión',
      message: 'Ha ocurrido un error de red. Por favor, verifica tu conexión e intenta nuevamente.',
      duration: 8000,
    })
  }

  retry = () => {
    this.setState({ hasError: false, error: null })
  }

  render() {
    if (this.state.hasError && this.state.error) {
      // Render custom fallback if provided
      if (this.props.fallback) {
        const FallbackComponent = this.props.fallback
        return <FallbackComponent error={this.state.error} retry={this.retry} />
      }

      // Default network error fallback
      return (
        <div className="flex flex-col items-center justify-center min-h-[200px] p-6 text-center">
          <div className="mb-4">
            <svg
              className="w-12 h-12 text-gray-400 mx-auto"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Error de conexión
          </h3>
          <p className="text-gray-600 mb-4">
            No se pudo conectar con el servidor. Verifica tu conexión a internet.
          </p>
          <button
            onClick={this.retry}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Reintentar
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

/**
 * Hook for handling offline mutations
 * Queues mutations when offline and executes them when online
 */
export const useOfflineMutations = () => {
  const [offlineQueue, setOfflineQueue] = useState<Array<{
    id: string
    mutationFn: () => Promise<any>
    variables: any
    timestamp: number
  }>>([])
  
  const { isOnline } = useNetworkStatus()
  const queryClient = useQueryClient()

  // Process offline queue when coming back online
  useEffect(() => {
    if (isOnline && offlineQueue.length > 0) {
      console.log(`🔄 Processing ${offlineQueue.length} offline mutations`)
      
      const processQueue = async () => {
        const results = []
        
        for (const queuedMutation of offlineQueue) {
          try {
            const result = await queuedMutation.mutationFn()
            results.push({ id: queuedMutation.id, success: true, result })
          } catch (error) {
            console.error(`[ERROR] Offline mutation ${queuedMutation.id} failed:`, error)
            results.push({ id: queuedMutation.id, success: false, error })
          }
        }
        
        // Clear the queue
        setOfflineQueue([])
        
        // Show summary notification
        const successCount = results.filter(r => r.success).length
        const failureCount = results.length - successCount
        
        if (successCount > 0) {
          useAppStore.getState().addNotification({
            type: 'success',
            title: 'Operaciones sincronizadas',
            message: `${successCount} operación(es) se completaron correctamente.`,
            duration: 4000,
          })
        }
        
        if (failureCount > 0) {
          useAppStore.getState().addNotification({
            type: 'warning',
            title: 'Algunas operaciones fallaron',
            message: `${failureCount} operación(es) no se pudieron completar.`,
            duration: 6000,
          })
        }
      }
      
      processQueue()
    }
  }, [isOnline, offlineQueue])

  // Queue mutation for offline execution
  const queueMutation = useCallback((
    mutationFn: () => Promise<any>,
    variables: any,
    id?: string
  ) => {
    const mutationId = id || `mutation_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    
    setOfflineQueue(prev => [...prev, {
      id: mutationId,
      mutationFn,
      variables,
      timestamp: Date.now(),
    }])
    
    console.log(`📝 Queued offline mutation: ${mutationId}`)
    
    // Show notification
    useAppStore.getState().addNotification({
      type: 'info',
      title: 'Operación en cola',
      message: 'La operación se ejecutará cuando se restaure la conexión.',
      duration: 3000,
    })
    
    return mutationId
  }, [])

  // Clear offline queue
  const clearQueue = useCallback(() => {
    setOfflineQueue([])
  }, [])

  return {
    offlineQueue,
    queueSize: offlineQueue.length,
    queueMutation,
    clearQueue,
    isOnline,
  }
}

export default useNetworkRecovery