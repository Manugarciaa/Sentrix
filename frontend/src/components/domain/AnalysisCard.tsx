import React from 'react'
import { useNavigate } from 'react-router-dom'
import { MapPin, Calendar, Image as ImageIcon, AlertCircle, CheckCircle2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import { RiskBadge } from './RiskBadge'
import { Badge } from '@/components/ui/Badge'
import type { Analysis } from '@/types'
import { env } from '@/lib/config'

// Helper function to normalize image URLs
const normalizeImageUrl = (url: string | undefined): string | undefined => {
  if (!url) return undefined

  // Si ya es una URL completa (http/https), devolverla tal cual
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }

  // Verificar que supabaseUrl esté configurado
  if (!env.supabaseUrl) {
    console.error('VITE_SUPABASE_URL no está configurado en .env')
    return undefined
  }

  // Si es una ruta relativa temporal (temp/...), construir URL de Supabase Storage
  if (url.startsWith('temp/')) {
    const filename = url.replace('temp/', '')
    return `${env.supabaseUrl}/storage/v1/object/public/sentrix-images/${filename}`
  }

  // Si comienza con "original_", usar bucket sentrix-images
  if (url.startsWith('original_')) {
    return `${env.supabaseUrl}/storage/v1/object/public/sentrix-images/${url}`
  }

  // Si comienza con "processed_", usar bucket sentrix-processed
  if (url.startsWith('processed_')) {
    return `${env.supabaseUrl}/storage/v1/object/public/sentrix-processed/${url}`
  }

  // Si es un UUID (archivo de Supabase sin prefijo), asumir bucket sentrix-images
  if (url.match(/^[0-9a-f-]+\.(jpg|jpeg|png|webp|tiff)$/i)) {
    return `${env.supabaseUrl}/storage/v1/object/public/sentrix-images/${url}`
  }

  // Si es un nombre de archivo SENTRIX_..., asumir bucket sentrix-images
  if (url.startsWith('SENTRIX_')) {
    return `${env.supabaseUrl}/storage/v1/object/public/sentrix-images/${url}`
  }

  // Por defecto, asumir que es del bucket sentrix-images
  return `${env.supabaseUrl}/storage/v1/object/public/sentrix-images/${url}`
}

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

  // Usar imagen procesada si existe, sino la original (normalizar URLs)
  const displayImage = normalizeImageUrl(analysis.processed_image_url || analysis.image_url)
  const [imageError, setImageError] = React.useState(false)

  return (
    <div
      className={cn(
        'group bg-card rounded-lg border border-border overflow-hidden shadow-sm',
        'hover:shadow-md hover:border-primary/40 dark:hover:border-primary/50',
        'transition-all duration-300 cursor-pointer',
        className
      )}
      onClick={handleViewDetail}
    >
      <div className="flex gap-3 p-3">
        {/* Image Thumbnail - Más pequeña */}
        <div className="relative w-24 h-24 bg-muted overflow-hidden rounded-md flex-shrink-0">
          {displayImage && !imageError ? (
            <img
              src={displayImage}
              alt={analysis.processed_image_url ? "Análisis con detecciones" : "Análisis"}
              className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
              onError={() => setImageError(true)}
              loading="lazy"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-muted to-muted/50">
              <ImageIcon className="h-8 w-8 text-muted-foreground/40" />
            </div>
          )}
          {analysis.processed_image_url && !imageError && (
            <div className="absolute top-1 left-1">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            </div>
          )}
        </div>

        {/* Content - Más compacto */}
        <div className="flex-1 min-w-0 flex flex-col justify-between">
          {/* Header */}
          <div>
            <div className="flex items-start justify-between gap-2 mb-1">
              <h3 className="text-sm font-semibold text-foreground truncate">
                Análisis #{analysis.id.slice(0, 8)}
              </h3>
              {analysis.risk_assessment?.level && (
                <RiskBadge level={analysis.risk_assessment.level} size="sm" />
              )}
            </div>

            {/* Metadata compacta */}
            <div className="flex items-center gap-3 text-xs text-muted-foreground mb-1">
              <div className="flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                <span>{formatDate(analysis.created_at)}</span>
              </div>
              {detectionCount > 0 && (
                <div className="flex items-center gap-1 text-red-600 dark:text-red-400 font-medium">
                  <AlertCircle className="h-3 w-3" />
                  <span>{detectionCount}</span>
                </div>
              )}
            </div>

            {hasLocation && (
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <MapPin className="h-3 w-3" />
                <span className="truncate">
                  {analysis.location.latitude.toFixed(4)}, {analysis.location.longitude.toFixed(4)}
                </span>
              </div>
            )}
          </div>

          {/* Footer con modelo */}
          {analysis.model_used && (
            <div className="text-xs text-muted-foreground truncate">
              <span className="font-medium">{analysis.model_used}</span>
              {analysis.processing_time_ms && (
                <span className="ml-2">• {(analysis.processing_time_ms / 1000).toFixed(1)}s</span>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default AnalysisCard
