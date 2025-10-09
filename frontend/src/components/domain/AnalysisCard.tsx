import React from 'react'
import { useNavigate } from 'react-router-dom'
import { MapPin, Calendar, Image as ImageIcon, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import { RiskBadge } from './RiskBadge'
import type { Analysis } from '@/types'

export interface AnalysisCardProps {
  analysis: Analysis
  onViewDetail?: () => void
  onValidate?: () => void
  className?: string
}

export const AnalysisCard: React.FC<AnalysisCardProps> = ({
  analysis,
  onViewDetail,
  onValidate,
  className,
}) => {
  const navigate = useNavigate()

  const handleViewDetail = () => {
    if (onViewDetail) {
      onViewDetail()
    } else {
      navigate(`/app/analysis/${analysis.id}`)
    }
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const hasLocation = analysis.location?.has_location ?? false
  const detectionCount = analysis.detections?.length || 0
  const highRiskCount = analysis.detections?.filter(d => d.risk_level === 'ALTO').length || 0

  return (
    <div
      className={cn(
        'bg-white rounded-xl border border-gray-200 overflow-hidden transition-all duration-300',
        'hover:shadow-lg hover:border-gray-300',
        className
      )}
    >
      {/* Image Thumbnail */}
      {analysis.image_filename && (
        <div className="relative h-48 bg-gray-100 overflow-hidden">
          <img
            src={`${analysis.image_filename}`}
            alt="Análisis"
            className="w-full h-full object-cover"
            onError={(e) => {
              e.currentTarget.src = '/images/placeholder-analysis.jpg'
            }}
          />
          <div className="absolute top-3 right-3">
            {analysis.risk_assessment?.level && (
              <RiskBadge level={analysis.risk_assessment.level} size="sm" />
            )}
          </div>
        </div>
      )}

      {/* Content */}
      <div className="p-5">
        {/* Header */}
        <div className="mb-4">
          <div className="flex items-start justify-between gap-2 mb-2">
            <h3 className="text-lg font-semibold text-gray-900 truncate">
              Análisis #{analysis.id.slice(0, 8)}
            </h3>
            {detectionCount > 0 && (
              <div className="flex items-center gap-1 px-2 py-1 bg-red-50 rounded-md shrink-0">
                <AlertCircle className="h-3.5 w-3.5 text-red-600" />
                <span className="text-xs font-medium text-red-600">
                  {detectionCount} detección{detectionCount !== 1 ? 'es' : ''}
                </span>
              </div>
            )}
          </div>

          {highRiskCount > 0 && (
            <p className="text-sm text-orange-600 font-medium">
              {highRiskCount} de alto riesgo
            </p>
          )}
        </div>

        {/* Metadata */}
        <div className="space-y-2 mb-4">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Calendar className="h-4 w-4" />
            <span>{formatDate(analysis.created_at)}</span>
          </div>

          {hasLocation && analysis.location?.latitude && analysis.location?.longitude && (
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <MapPin className="h-4 w-4" />
              <span className="truncate">
                {analysis.location.latitude.toFixed(4)}, {analysis.location.longitude.toFixed(4)}
              </span>
            </div>
          )}

          {analysis.image_size_bytes && (
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <ImageIcon className="h-4 w-4" />
              <span>
                {(analysis.image_size_bytes / 1024 / 1024).toFixed(2)} MB
              </span>
            </div>
          )}
        </div>

        {/* Model Info */}
        {analysis.model_used && (
          <div className="mb-4 p-3 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-600">
              Modelo: <span className="font-medium text-gray-900">{analysis.model_used}</span>
            </p>
            {analysis.processing_time_ms && (
              <p className="text-xs text-gray-600 mt-1">
                Tiempo: {(analysis.processing_time_ms / 1000).toFixed(2)}s
              </p>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-2">
          <Button
            onClick={handleViewDetail}
            className="flex-1 bg-gradient-to-r from-primary-600 to-cyan-600 hover:from-primary-700 hover:to-cyan-700"
            size="sm"
          >
            Ver Detalle
          </Button>
          {onValidate && (
            <Button
              onClick={onValidate}
              variant="outline"
              size="sm"
            >
              Validar
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}

export default AnalysisCard
