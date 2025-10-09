import React from 'react'
import {
  Image as ImageIcon,
  CheckCircle,
  XCircle,
  Loader2,
  Clock,
  AlertCircle,
  Trash2
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import { ProgressBar } from '@/components/ui/ProgressBar'
import type { BatchItem } from '@/store/upload'

export interface BatchQueueListProps {
  items: BatchItem[]
  onRemove?: (id: string) => void
  className?: string
}

export const BatchQueueList: React.FC<BatchQueueListProps> = ({
  items,
  onRemove,
  className,
}) => {
  const getStatusIcon = (status: BatchItem['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-600" />
      case 'processing':
        return <Loader2 className="h-5 w-5 text-primary-600 animate-spin" />
      case 'pending':
      default:
        return <Clock className="h-5 w-5 text-gray-400" />
    }
  }

  const getStatusLabel = (status: BatchItem['status']) => {
    switch (status) {
      case 'completed':
        return 'Completado'
      case 'failed':
        return 'Error'
      case 'processing':
        return 'Procesando'
      case 'pending':
      default:
        return 'En cola'
    }
  }

  const getStatusColor = (status: BatchItem['status']) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-50 border-green-200'
      case 'failed':
        return 'text-red-600 bg-red-50 border-red-200'
      case 'processing':
        return 'text-primary-600 bg-primary-50 border-primary-200'
      case 'pending':
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const formatFileSize = (bytes: number) => {
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  }

  if (items.length === 0) {
    return (
      <div className={cn('bg-gray-50 rounded-xl border-2 border-dashed border-gray-300 p-8', className)}>
        <div className="text-center">
          <div className="mx-auto w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center mb-3">
            <ImageIcon className="h-6 w-6 text-gray-400" />
          </div>
          <p className="text-sm text-gray-600">No hay archivos en la cola</p>
        </div>
      </div>
    )
  }

  const pendingCount = items.filter(i => i.status === 'pending').length
  const processingCount = items.filter(i => i.status === 'processing').length
  const completedCount = items.filter(i => i.status === 'completed').length
  const failedCount = items.filter(i => i.status === 'failed').length

  return (
    <div className={cn('space-y-4', className)}>
      {/* Summary */}
      <div className="grid grid-cols-4 gap-3">
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
          <p className="text-xs text-gray-600 mb-1">En cola</p>
          <p className="text-2xl font-bold text-gray-900">{pendingCount}</p>
        </div>
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-3">
          <p className="text-xs text-primary-700 mb-1">Procesando</p>
          <p className="text-2xl font-bold text-primary-900">{processingCount}</p>
        </div>
        <div className="bg-green-50 border border-green-200 rounded-lg p-3">
          <p className="text-xs text-green-700 mb-1">Completados</p>
          <p className="text-2xl font-bold text-green-900">{completedCount}</p>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <p className="text-xs text-red-700 mb-1">Errores</p>
          <p className="text-2xl font-bold text-red-900">{failedCount}</p>
        </div>
      </div>

      {/* Items List */}
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {items.map((item) => (
          <div
            key={item.id}
            className={cn(
              'bg-white border rounded-lg p-4 transition-all',
              getStatusColor(item.status)
            )}
          >
            <div className="flex items-start gap-3">
              {/* Icon */}
              <div className="shrink-0 w-10 h-10 bg-white rounded-lg flex items-center justify-center">
                <ImageIcon className="h-5 w-5 text-gray-600" />
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-gray-900 truncate">
                      {item.file.name}
                    </p>
                    <p className="text-xs text-gray-600">
                      {formatFileSize(item.file.size)}
                    </p>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    {/* Status Badge */}
                    <div className="flex items-center gap-1">
                      {getStatusIcon(item.status)}
                      <span className="text-xs font-medium">
                        {getStatusLabel(item.status)}
                      </span>
                    </div>

                    {/* Remove Button */}
                    {onRemove && item.status !== 'processing' && (
                      <Button
                        onClick={() => onRemove(item.id)}
                        variant="ghost"
                        size="sm"
                        className="text-gray-400 hover:text-red-600"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>

                {/* Progress Bar for Processing */}
                {item.status === 'processing' && (
                  <ProgressBar
                    value={item.progress}
                    variant="primary"
                    showLabel={true}
                    size="sm"
                  />
                )}

                {/* Error Message */}
                {item.status === 'failed' && item.error && (
                  <div className="mt-2 flex items-start gap-2 text-xs text-red-800">
                    <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                    <span>{item.error}</span>
                  </div>
                )}

                {/* Success Info */}
                {item.status === 'completed' && item.result && (
                  <div className="mt-2 flex items-center gap-4 text-xs text-green-800">
                    <span>
                      ✓ {item.result.detections?.length || 0} detección
                      {item.result.detections?.length !== 1 ? 'es' : ''}
                    </span>
                    {item.result.analysis?.processing_time_ms && (
                      <span>
                        • {(item.result.analysis.processing_time_ms / 1000).toFixed(1)}s
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default BatchQueueList
