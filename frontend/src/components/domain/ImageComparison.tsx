import React, { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Eye, EyeOff } from 'lucide-react'

export interface ImageComparisonProps {
  originalUrl: string
  processedUrl?: string
  altText?: string
  className?: string
}

export const ImageComparison: React.FC<ImageComparisonProps> = ({
  originalUrl,
  processedUrl,
  altText = 'Análisis',
  className = ''
}) => {
  const [showProcessed, setShowProcessed] = useState(!!processedUrl)

  // Si no hay imagen procesada, mostrar solo la original
  if (!processedUrl) {
    return (
      <div className={className}>
        <img
          src={originalUrl}
          alt={altText}
          className="w-full rounded-lg border-2 border-border"
        />
      </div>
    )
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Imagen */}
      <div className="relative">
        <img
          src={showProcessed ? processedUrl : originalUrl}
          alt={showProcessed ? `${altText} - Procesada` : `${altText} - Original`}
          className="w-full rounded-lg border-2 border-border transition-opacity duration-300"
        />

        {/* Indicador */}
        <div className="absolute top-3 left-3">
          <Badge
            className={
              showProcessed
                ? 'bg-blue-500 dark:bg-blue-600 text-white'
                : 'bg-gray-500 dark:bg-gray-600 text-white'
            }
          >
            {showProcessed ? 'Con detecciones' : 'Original'}
          </Badge>
        </div>
      </div>

      {/* Toggle Button */}
      <div className="flex justify-center">
        <Button
          variant="outline"
          onClick={() => setShowProcessed(!showProcessed)}
          className="gap-2"
        >
          {showProcessed ? (
            <>
              <EyeOff className="h-4 w-4" />
              Ver Original
            </>
          ) : (
            <>
              <Eye className="h-4 w-4" />
              Ver Detecciones
            </>
          )}
        </Button>
      </div>

      {/* Descripción */}
      {showProcessed && (
        <p className="text-sm text-muted-foreground text-center">
          Las detecciones están marcadas con polígonos y porcentajes de confianza
        </p>
      )}
    </div>
  )
}

export default ImageComparison
