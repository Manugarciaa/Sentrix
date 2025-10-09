import React, { useState, useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'

export interface SliderProps {
  value: number
  onChange: (value: number) => void
  min?: number
  max?: number
  step?: number
  label?: string
  showValue?: boolean
  showMinMax?: boolean
  disabled?: boolean
  className?: string
  formatValue?: (value: number) => string
}

export const Slider: React.FC<SliderProps> = ({
  value,
  onChange,
  min = 0,
  max = 100,
  step = 1,
  label,
  showValue = true,
  showMinMax = false,
  disabled = false,
  className,
  formatValue = (v) => v.toString(),
}) => {
  const [isDragging, setIsDragging] = useState(false)
  const sliderRef = useRef<HTMLDivElement>(null)

  const percentage = ((value - min) / (max - min)) * 100

  const handleMouseDown = (e: React.MouseEvent) => {
    if (disabled) return
    setIsDragging(true)
    updateValue(e.clientX)
  }

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging || disabled) return
    updateValue(e.clientX)
  }

  const handleMouseUp = () => {
    setIsDragging(false)
  }

  const updateValue = (clientX: number) => {
    if (!sliderRef.current) return

    const rect = sliderRef.current.getBoundingClientRect()
    const x = Math.max(0, Math.min(clientX - rect.left, rect.width))
    const percentage = x / rect.width
    const rawValue = min + percentage * (max - min)

    // Round to nearest step
    const steppedValue = Math.round(rawValue / step) * step
    const clampedValue = Math.max(min, Math.min(max, steppedValue))

    onChange(clampedValue)
  }

  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove)
      window.addEventListener('mouseup', handleMouseUp)

      return () => {
        window.removeEventListener('mousemove', handleMouseMove)
        window.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [isDragging])

  return (
    <div className={cn('space-y-2', className)}>
      {/* Label and Value */}
      {(label || showValue) && (
        <div className="flex items-center justify-between">
          {label && (
            <label className="text-sm font-medium text-gray-700">
              {label}
            </label>
          )}
          {showValue && (
            <span className="text-sm font-semibold text-gray-900">
              {formatValue(value)}
            </span>
          )}
        </div>
      )}

      {/* Slider Track */}
      <div
        ref={sliderRef}
        onMouseDown={handleMouseDown}
        className={cn(
          'relative h-2 bg-gray-200 rounded-full cursor-pointer',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      >
        {/* Progress */}
        <div
          className={cn(
            'absolute top-0 left-0 h-full rounded-full transition-all',
            disabled ? 'bg-gray-400' : 'bg-gradient-to-r from-primary-600 to-cyan-600'
          )}
          style={{ width: `${percentage}%` }}
        />

        {/* Thumb */}
        <div
          className={cn(
            'absolute top-1/2 -translate-y-1/2 w-5 h-5 rounded-full shadow-md transition-all',
            disabled
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-white border-2 border-primary-600 cursor-grab active:cursor-grabbing',
            isDragging && 'scale-110 shadow-lg'
          )}
          style={{ left: `calc(${percentage}% - 10px)` }}
        />
      </div>

      {/* Min/Max Labels */}
      {showMinMax && (
        <div className="flex items-center justify-between text-xs text-gray-600">
          <span>{formatValue(min)}</span>
          <span>{formatValue(max)}</span>
        </div>
      )}
    </div>
  )
}

export default Slider
