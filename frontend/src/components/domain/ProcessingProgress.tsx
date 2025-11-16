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
      return <XCircle className="h-6 w-6 text-destructive" />
    }

    if (stepData.completed) {
      return <CheckCircle className="h-6 w-6 text-green-600 dark:text-green-500" />
    }

    if (stepData.active) {
      return <Loader2 className="h-6 w-6 text-primary animate-spin" />
    }

    return <Icon className="h-6 w-6 text-muted-foreground" />
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
    <div className={cn('bg-card rounded-xl border border-border shadow-sm p-6', className)}>
      {/* Header */}
      {fileName && (
        <div className="flex items-start gap-3 mb-6">
          <div className="shrink-0 w-12 h-12 bg-primary/10 dark:bg-primary/20 rounded-lg flex items-center justify-center">
            <ImageIcon className="h-6 w-6 text-primary" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-foreground truncate">
              {fileName}
            </p>
            {fileSize && (
              <p className="text-xs text-muted-foreground">
                {formatFileSize(fileSize)}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Error Message */}
      {step === 'error' && error && (
        <div className="mb-6 p-4 bg-destructive/10 border-2 border-destructive/20 rounded-lg">
          <div className="flex items-start gap-2">
            <XCircle className="h-5 w-5 text-destructive shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-destructive mb-1">
                Error en el procesamiento
              </p>
              <p className="text-sm text-destructive/80">{error}</p>
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
                    ? 'bg-green-100 dark:bg-green-950'
                    : stepData.active
                    ? 'bg-primary/10 dark:bg-primary/20'
                    : 'bg-muted/50'
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
                      ? 'text-foreground'
                      : 'text-muted-foreground'
                  )}
                >
                  {stepData.label}
                </p>
                {stepData.active && step !== 'error' && (
                  <p className="text-xs text-muted-foreground">En progreso...</p>
                )}
                {stepData.completed && (
                  <p className="text-xs text-green-600 dark:text-green-500">✓ Completado</p>
                )}
              </div>
            </div>

            {/* Connector Line */}
            {index < steps.length - 1 && (
              <div className="absolute left-6 top-12 w-0.5 h-4 bg-border" />
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
          <p className="text-xs text-muted-foreground text-center">
            {progress < 100 ? 'Procesando...' : 'Finalizando...'}
          </p>
        </div>
      )}

      {/* Results */}
      {step === 'complete' && (
        <div className="grid grid-cols-2 gap-4 p-4 bg-green-50 dark:bg-green-950 border-2 border-green-200 dark:border-green-800 rounded-lg">
          {detectionCount !== undefined && (
            <div>
              <p className="text-xs text-green-700 dark:text-green-400 mb-1">Detecciones</p>
              <p className="text-2xl font-bold text-green-900 dark:text-green-100">{detectionCount}</p>
            </div>
          )}
          {processingTime !== undefined && (
            <div>
              <p className="text-xs text-green-700 dark:text-green-400 mb-1">Tiempo</p>
              <p className="text-2xl font-bold text-green-900 dark:text-green-100">
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
