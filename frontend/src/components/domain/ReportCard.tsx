import React from 'react'
import { FileText, Download, Eye, Trash2, Calendar, FileType, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'

export interface Report {
  id: string
  title: string
  type: 'summary' | 'detailed' | 'map' | 'statistics'
  format: 'pdf' | 'csv' | 'json'
  status: 'generating' | 'ready' | 'failed'
  created_at: string
  file_size?: number
  download_url?: string
  filters?: {
    date_from?: string
    date_to?: string
    risk_level?: string
    user_id?: number
  }
}

export interface ReportCardProps {
  report: Report
  onDownload?: (report: Report) => void
  onView?: (report: Report) => void
  onDelete?: (report: Report) => void
  className?: string
}

export const ReportCard: React.FC<ReportCardProps> = ({
  report,
  onDownload,
  onView,
  onDelete,
  className,
}) => {
  const getTypeLabel = (type: Report['type']) => {
    switch (type) {
      case 'summary':
        return 'Resumen'
      case 'detailed':
        return 'Detallado'
      case 'map':
        return 'Mapa'
      case 'statistics':
        return 'Estadísticas'
    }
  }

  const getFormatBadgeVariant = (format: Report['format']) => {
    switch (format) {
      case 'pdf':
        return 'danger'
      case 'csv':
        return 'success'
      case 'json':
        return 'info'
    }
  }

  const getStatusBadge = () => {
    switch (report.status) {
      case 'generating':
        return (
          <Badge variant="warning" className="gap-1">
            <Loader2 className="h-3 w-3 animate-spin" />
            Generando
          </Badge>
        )
      case 'ready':
        return <Badge variant="success">Listo</Badge>
      case 'failed':
        return <Badge variant="danger">Error</Badge>
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'N/A'
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  return (
    <div
      className={cn(
        'bg-white border border-gray-200 rounded-xl p-5 transition-all hover:shadow-md hover:border-gray-300',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-4">
        <div className="flex items-start gap-3 flex-1 min-w-0">
          {/* Icon */}
          <div className="shrink-0 w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
            <FileText className="h-5 w-5 text-primary-600 dark:text-primary" />
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-semibold text-gray-900 truncate">
              {report.title}
            </h3>
            <p className="text-xs text-gray-600">
              {getTypeLabel(report.type)}
            </p>
          </div>
        </div>

        {/* Status */}
        {getStatusBadge()}
      </div>

      {/* Metadata */}
      <div className="space-y-2 mb-4">
        <div className="flex items-center gap-2 text-xs text-gray-600">
          <Calendar className="h-3.5 w-3.5" />
          <span>{formatDate(report.created_at)}</span>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant={getFormatBadgeVariant(report.format)}>
            {report.format.toUpperCase()}
          </Badge>
          {report.file_size && (
            <span className="text-xs text-gray-600">
              {formatFileSize(report.file_size)}
            </span>
          )}
        </div>

        {/* Filters Applied */}
        {report.filters && (
          <div className="pt-2 border-t border-gray-200">
            <p className="text-xs text-gray-600 mb-1">Filtros aplicados:</p>
            <div className="flex flex-wrap gap-1">
              {report.filters.date_from && report.filters.date_to && (
                <Badge variant="default" className="text-xs">
                  {new Date(report.filters.date_from).toLocaleDateString('es-ES', { day: '2-digit', month: 'short' })} -{' '}
                  {new Date(report.filters.date_to).toLocaleDateString('es-ES', { day: '2-digit', month: 'short' })}
                </Badge>
              )}
              {report.filters.risk_level && (
                <Badge variant="default" className="text-xs">
                  Riesgo: {report.filters.risk_level}
                </Badge>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      {report.status === 'ready' && (
        <div className="flex items-center gap-2 pt-3 border-t border-gray-200">
          {onDownload && (
            <Button
              onClick={() => onDownload(report)}
              size="sm"
              className="flex-1 bg-gradient-to-r from-primary-600 to-cyan-600"
            >
              <Download className="h-3.5 w-3.5 mr-1" />
              Descargar
            </Button>
          )}

          {onView && report.format === 'pdf' && (
            <Button
              onClick={() => onView(report)}
              size="sm"
              variant="outline"
            >
              <Eye className="h-3.5 w-3.5" />
            </Button>
          )}

          {onDelete && (
            <Button
              onClick={() => onDelete(report)}
              size="sm"
              variant="ghost"
              className="text-red-600 hover:text-red-700 hover:bg-red-50"
            >
              <Trash2 className="h-3.5 w-3.5" />
            </Button>
          )}
        </div>
      )}

      {report.status === 'failed' && (
        <div className="pt-3 border-t border-gray-200">
          <p className="text-xs text-red-600">
            Error al generar el reporte. Intenta nuevamente.
          </p>
        </div>
      )}
    </div>
  )
}

export default ReportCard
