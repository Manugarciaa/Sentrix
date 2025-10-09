import React from 'react'
import { Upload, Image as ImageIcon, Cpu, CheckCircle, XCircle, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { ProgressBar } from '@/components/ui/ProgressBar'

export type ProcessingStep = 'upload' | 'processing' | 'complete' | 'error'

export interface ProcessingProgressProps {
  step: ProcessingStep
  progress: number
  fileName?: string
  fileSize?: number
  processingTime?: number
  detectionCount?: number
  error?: string
  className?: string
}

export const ProcessingProgress: React.FC<ProcessingProgressProps> = ({
  step,
  progress,
  fileName,
  fileSize,
  processingTime,
  detectionCount,
  error,
  className,
}) => {
  const steps = [
    {
      id: 'upload',
      label: 'Subiendo imagen',
      icon: Upload,
      active: step === 'upload',
      completed: ['processing', 'complete'].includes(step),
    },
    {
      id: 'processing',
      label: 'Analizando con IA',
      icon: Cpu,
      active: step === 'processing',
      completed: step === 'complete',
    },
    {
      id: 'complete',
      label: 'Completado',
      icon: CheckCircle,
      active: step === 'complete',
      completed: step === 'complete',
    },
  ]

  const getStepIcon = (stepData: typeof steps[0]) => {
    const Icon = stepData.icon

    if (step === 'error') {
      return <XCircle className="h-6 w-6 text-red-600" />
    }

    if (stepData.completed) {
      return <CheckCircle className="h-6 w-6 text-green-600" />
    }

    if (stepData.active) {
      return <Loader2 className="h-6 w-6 text-primary-600 animate-spin" />
    }

    return <Icon className="h-6 w-6 text-gray-400" />
  }

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return ''
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  }

  const formatTime = (ms?: number) => {
    if (!ms) return ''
    return (ms / 1000).toFixed(1) + 's'
  }

  return (
    <div className={cn('bg-white rounded-xl border border-gray-200 p-6', className)}>
      {/* Header */}
      {fileName && (
        <div className="flex items-start gap-3 mb-6">
          <div className="shrink-0 w-12 h-12 bg-primary-50 rounded-lg flex items-center justify-center">
            <ImageIcon className="h-6 w-6 text-primary-600" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-gray-900 truncate">
              {fileName}
            </p>
            {fileSize && (
              <p className="text-xs text-gray-600">
                {formatFileSize(fileSize)}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Error Message */}
      {step === 'error' && error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start gap-2">
            <XCircle className="h-5 w-5 text-red-600 shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-red-900 mb-1">
                Error en el procesamiento
              </p>
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Progress Steps */}
      <div className="space-y-4 mb-6">
        {steps.map((stepData, index) => (
          <div key={stepData.id} className="relative">
            <div className="flex items-center gap-4">
              {/* Icon */}
              <div
                className={cn(
                  'shrink-0 w-12 h-12 rounded-full flex items-center justify-center transition-all',
                  stepData.completed
                    ? 'bg-green-100'
                    : stepData.active
                    ? 'bg-primary-100'
                    : 'bg-gray-100'
                )}
              >
                {getStepIcon(stepData)}
              </div>

              {/* Label */}
              <div className="flex-1">
                <p
                  className={cn(
                    'text-sm font-medium',
                    stepData.completed || stepData.active
                      ? 'text-gray-900'
                      : 'text-gray-500'
                  )}
                >
                  {stepData.label}
                </p>
                {stepData.active && step !== 'error' && (
                  <p className="text-xs text-gray-600">En progreso...</p>
                )}
                {stepData.completed && (
                  <p className="text-xs text-green-600">✓ Completado</p>
                )}
              </div>
            </div>

            {/* Connector Line */}
            {index < steps.length - 1 && (
              <div className="absolute left-6 top-12 w-0.5 h-4 bg-gray-200" />
            )}
          </div>
        ))}
      </div>

      {/* Progress Bar */}
      {step !== 'error' && step !== 'complete' && (
        <div className="mb-6">
          <ProgressBar
            value={progress}
            variant="primary"
            showLabel={true}
            className="mb-2"
          />
          <p className="text-xs text-gray-600 text-center">
            {progress < 100 ? 'Procesando...' : 'Finalizando...'}
          </p>
        </div>
      )}

      {/* Results */}
      {step === 'complete' && (
        <div className="grid grid-cols-2 gap-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          {detectionCount !== undefined && (
            <div>
              <p className="text-xs text-green-700 mb-1">Detecciones</p>
              <p className="text-2xl font-bold text-green-900">{detectionCount}</p>
            </div>
          )}
          {processingTime !== undefined && (
            <div>
              <p className="text-xs text-green-700 mb-1">Tiempo</p>
              <p className="text-2xl font-bold text-green-900">
                {formatTime(processingTime)}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ProcessingProgress
