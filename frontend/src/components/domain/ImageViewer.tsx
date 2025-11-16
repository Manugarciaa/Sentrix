import React, { useState, useRef, useEffect } from 'react'
import { ZoomIn, ZoomOut, Maximize2, Minimize2, RotateCw, Download } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import type { Detection } from '@/types'

export interface ImageViewerProps {
  imageUrl: string
  detections?: Detection[]
  showDetections?: boolean
  className?: string
  onDetectionClick?: (detection: Detection) => void
  alt?: string
}

export const ImageViewer: React.FC<ImageViewerProps> = ({
  imageUrl,
  detections = [],
  showDetections = true,
  className,
  onDetectionClick,
  alt = 'Análisis de imagen',
}) => {
  const [zoom, setZoom] = useState(100)
  const [rotation, setRotation] = useState(0)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [imageDimensions, setImageDimensions] = useState({ width: 0, height: 0 })
  const [selectedDetection, setSelectedDetection] = useState<string | null>(null)
  const [imageError, setImageError] = useState(false)
  const imageRef = useRef<HTMLImageElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    setImageError(false) // Reset error state when imageUrl changes
    const img = new Image()
    img.onload = () => {
      setImageDimensions({ width: img.naturalWidth, height: img.naturalHeight })
    }
    img.onerror = () => {
      setImageError(true)
    }
    img.src = imageUrl
  }, [imageUrl])

  const handleZoomIn = () => {
    setZoom((prev) => Math.min(prev + 25, 300))
  }

  const handleZoomOut = () => {
    setZoom((prev) => Math.max(prev - 25, 25))
  }

  const handleResetZoom = () => {
    setZoom(100)
    setRotation(0)
  }

  const handleRotate = () => {
    setRotation((prev) => (prev + 90) % 360)
  }

  const handleFullscreen = () => {
    if (!containerRef.current) return

    if (!isFullscreen) {
      if (containerRef.current.requestFullscreen) {
        containerRef.current.requestFullscreen()
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen()
      }
    }
    setIsFullscreen(!isFullscreen)
  }

  const handleDownload = () => {
    const link = document.createElement('a')
    link.href = imageUrl
    link.download = `analysis-${Date.now()}.jpg`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handleDetectionClick = (detection: Detection) => {
    setSelectedDetection(detection.id)
    onDetectionClick?.(detection)
  }

  // Convert polygon points to SVG path
  const polygonToPath = (polygon: number[][]): string => {
    if (!polygon || polygon.length === 0) return ''

    const points = polygon.map((point, index) => {
      const [x, y] = point
      return `${index === 0 ? 'M' : 'L'} ${x} ${y}`
    }).join(' ')

    return `${points} Z`
  }

  // Get color based on risk level
  const getRiskColor = (riskLevel: string): string => {
    switch (riskLevel) {
      case 'ALTO':
        return '#ef4444' // red-500
      case 'MEDIO':
        return '#f59e0b' // amber-500
      case 'BAJO':
        return '#10b981' // green-500
      default:
        return '#6b7280' // gray-500
    }
  }

  return (
    <div ref={containerRef} className={cn('bg-gray-900 rounded-xl overflow-hidden', className)}>
      {/* Controls */}
      <div className="bg-gray-800 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Button
            onClick={handleZoomOut}
            size="sm"
            variant="ghost"
            className="text-white hover:bg-gray-700"
            disabled={zoom <= 25}
          >
            <ZoomOut className="h-4 w-4" />
          </Button>
          <span className="text-sm text-white font-medium min-w-[60px] text-center">
            {zoom}%
          </span>
          <Button
            onClick={handleZoomIn}
            size="sm"
            variant="ghost"
            className="text-white hover:bg-gray-700"
            disabled={zoom >= 300}
          >
            <ZoomIn className="h-4 w-4" />
          </Button>
          <div className="w-px h-6 bg-gray-600 mx-2" />
          <Button
            onClick={handleRotate}
            size="sm"
            variant="ghost"
            className="text-white hover:bg-gray-700"
          >
            <RotateCw className="h-4 w-4" />
          </Button>
          <Button
            onClick={handleResetZoom}
            size="sm"
            variant="ghost"
            className="text-white hover:bg-gray-700"
          >
            Reset
          </Button>
        </div>

        <div className="flex items-center gap-2">
          <Button
            onClick={handleDownload}
            size="sm"
            variant="ghost"
            className="text-white hover:bg-gray-700"
          >
            <Download className="h-4 w-4" />
          </Button>
          <Button
            onClick={handleFullscreen}
            size="sm"
            variant="ghost"
            className="text-white hover:bg-gray-700"
          >
            {isFullscreen ? (
              <Minimize2 className="h-4 w-4" />
            ) : (
              <Maximize2 className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>

      {/* Image Container */}
      <div className="relative overflow-auto bg-gray-900" style={{ height: '600px' }}>
        <div className="flex items-center justify-center min-h-full p-4">
          <div className="relative inline-block">
            {!imageError ? (
              <img
                ref={imageRef}
                src={imageUrl}
                alt={alt}
                className="max-w-none transition-transform duration-200"
                style={{
                  width: `${zoom}%`,
                  transform: `rotate(${rotation}deg)`,
                }}
                onError={() => setImageError(true)}
              />
            ) : (
              <div className="flex items-center justify-center w-full h-96 bg-muted">
                <div className="text-center space-y-2">
                  <svg
                    className="mx-auto h-24 w-24 text-muted-foreground/40"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                  </svg>
                  <p className="text-sm font-medium text-foreground">Error al cargar imagen</p>
                  <p className="text-xs text-muted-foreground">La imagen no está disponible</p>
                </div>
              </div>
            )}

            {/* SVG Overlay for Detections */}
            {showDetections && detections.length > 0 && imageDimensions.width > 0 && (
              <svg
                className="absolute top-0 left-0 pointer-events-none"
                style={{
                  width: `${zoom}%`,
                  transform: `rotate(${rotation}deg)`,
                }}
                viewBox={`0 0 ${imageDimensions.width} ${imageDimensions.height}`}
                preserveAspectRatio="xMidYMid meet"
              >
                {detections.map((detection) => {
                  const color = getRiskColor(detection.risk_level)
                  const isSelected = selectedDetection === detection.id

                  return (
                    <g key={detection.id}>
                      {/* Polygon */}
                      <path
                        d={polygonToPath(detection.polygon)}
                        fill={color}
                        fillOpacity={isSelected ? 0.4 : 0.2}
                        stroke={color}
                        strokeWidth={isSelected ? 4 : 2}
                        className="pointer-events-auto cursor-pointer transition-all"
                        onClick={() => handleDetectionClick(detection)}
                      />

                      {/* Label */}
                      {detection.polygon && detection.polygon.length > 0 && (
                        <text
                          x={detection.polygon[0][0]}
                          y={detection.polygon[0][1] - 10}
                          fill={color}
                          fontSize="16"
                          fontWeight="bold"
                          className="pointer-events-none"
                          style={{ textShadow: '0 0 4px rgba(0,0,0,0.8)' }}
                        >
                          {(detection.confidence * 100).toFixed(0)}%
                        </text>
                      )}
                    </g>
                  )
                })}
              </svg>
            )}
          </div>
        </div>
      </div>

      {/* Detection Info Bar */}
      {showDetections && detections.length > 0 && (
        <div className="bg-gray-800 px-4 py-2 flex items-center justify-between text-xs text-gray-400">
          <span>{detections.length} detección{detections.length !== 1 ? 'es' : ''} encontrada{detections.length !== 1 ? 's' : ''}</span>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: '#ef4444' }} />
              <span>Alto</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: '#f59e0b' }} />
              <span>Medio</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: '#10b981' }} />
              <span>Bajo</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ImageViewer
