import React from 'react'
import { AlertCircle, MapPin, CheckCircle, XCircle, Clock } from 'lucide-react'
import { cn } from '@/lib/utils'
import { RiskBadge } from './RiskBadge'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import type { Detection } from '@/types'

export interface DetectionCardProps {
  detection: Detection
  onValidate?: (detectionId: string, status: 'validated_positive' | 'validated_negative') => void
  onViewOnMap?: (detection: Detection) => void
  showActions?: boolean
  className?: string
}

export const DetectionCard: React.FC<DetectionCardProps> = ({
  detection,
  onValidate,
  onViewOnMap,
  showActions = true,
  className,
}) => {
  const getValidationBadge = () => {
    switch (detection.validation_status) {
      case 'validated_positive':
        return <Badge variant="success" className="gap-1"><CheckCircle className="h-3 w-3" />Validado</Badge>
      case 'validated_negative':
        return <Badge variant="danger" className="gap-1"><XCircle className="h-3 w-3" />Rechazado</Badge>
      case 'requires_review':
        return <Badge variant="warning" className="gap-1"><AlertCircle className="h-3 w-3" />Revisión</Badge>
      default:
        return <Badge variant="default" className="gap-1"><Clock className="h-3 w-3" />Pendiente</Badge>
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

  const hasLocation = detection.location?.has_location ?? false

  return (
    <div
      className={cn(
        'bg-white rounded-lg border border-gray-200 p-4 transition-all duration-200',
        'hover:shadow-md hover:border-gray-300',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="text-sm font-semibold text-gray-900 truncate">
              {detection.breeding_site_type || detection.class_name}
            </h4>
            <RiskBadge level={detection.risk_level} size="sm" />
          </div>
          <p className="text-xs text-gray-600">
            ID: {detection.id.slice(0, 12)}...
          </p>
        </div>
        {getValidationBadge()}
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-3 mb-3">
        <div className="bg-gray-50 rounded-lg p-2">
          <p className="text-xs text-gray-600 mb-0.5">Confianza</p>
          <div className="flex items-baseline gap-1">
            <p className="text-lg font-bold text-gray-900">
              {(detection.confidence * 100).toFixed(1)}%
            </p>
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-2">
          <p className="text-xs text-gray-600 mb-0.5">Área</p>
          <div className="flex items-baseline gap-1">
            <p className="text-lg font-bold text-gray-900">
              {detection.mask_area?.toFixed(0) || detection.area_square_pixels?.toFixed(0) || 'N/A'}
            </p>
            <span className="text-xs text-gray-600">px²</span>
          </div>
        </div>
      </div>

      {/* Location */}
      {hasLocation && detection.location?.latitude && detection.location?.longitude && (
        <div className="mb-3 p-2 bg-blue-50 rounded-lg">
          <div className="flex items-center gap-2 text-xs text-blue-900">
            <MapPin className="h-3.5 w-3.5" />
            <span className="truncate">
              {detection.location.latitude.toFixed(6)}, {detection.location.longitude.toFixed(6)}
            </span>
          </div>
        </div>
      )}

      {/* Validation Notes */}
      {detection.validation_notes && (
        <div className="mb-3 p-2 bg-amber-50 border border-amber-200 rounded-lg">
          <p className="text-xs text-amber-900">
            <strong>Nota:</strong> {detection.validation_notes}
          </p>
        </div>
      )}

      {/* Validation Info */}
      {detection.validated_at && (
        <p className="text-xs text-gray-600 mb-3">
          Validado el {formatDate(detection.validated_at)}
        </p>
      )}

      {/* Actions */}
      {showActions && onValidate && detection.validation_status === 'pending_validation' && (
        <div className="flex gap-2 pt-3 border-t border-gray-200">
          <Button
            onClick={() => onValidate(detection.id, 'validated_positive')}
            size="sm"
            className="flex-1 bg-green-600 hover:bg-green-700"
          >
            <CheckCircle className="h-3.5 w-3.5 mr-1" />
            Validar
          </Button>
          <Button
            onClick={() => onValidate(detection.id, 'validated_negative')}
            size="sm"
            variant="outline"
            className="flex-1 text-red-600 border-red-300 hover:bg-red-50"
          >
            <XCircle className="h-3.5 w-3.5 mr-1" />
            Rechazar
          </Button>
        </div>
      )}

      {/* View on Map */}
      {onViewOnMap && hasLocation && (
        <Button
          onClick={() => onViewOnMap(detection)}
          size="sm"
          variant="outline"
          className="w-full mt-2"
        >
          <MapPin className="h-3.5 w-3.5 mr-1" />
          Ver en Mapa
        </Button>
      )}
    </div>
  )
}

export default DetectionCard
