import React from 'react'
import { cn } from '@/lib/utils'
import { Progress } from '@/components/ui/progress'

export interface ProgressBarProps {
  value: number
  max?: number
  className?: string
  size?: 'sm' | 'md' | 'lg'
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'primary'
  showLabel?: boolean
  label?: string
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  className,
  size = 'md',
  variant = 'primary',
  showLabel = false,
  label,
}) => {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100))

  const sizes = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  }

  const variants = {
    default: '[&>div]:bg-muted-foreground',
    success: '[&>div]:bg-green-600 dark:[&>div]:bg-green-500',
    warning: '[&>div]:bg-yellow-600 dark:[&>div]:bg-yellow-500',
    danger: '[&>div]:bg-destructive',
    primary: '[&>div]:bg-gradient-to-r [&>div]:from-primary [&>div]:to-primary/80',
  }

  return (
    <div className={cn('w-full', className)}>
      {(showLabel || label) && (
        <div className="flex items-center justify-between mb-1.5">
          {label && (
            <span className="text-sm font-medium text-foreground">{label}</span>
          )}
          {showLabel && (
            <span className="text-sm font-medium text-muted-foreground">
              {Math.round(percentage)}%
            </span>
          )}
        </div>
      )}

      <Progress
        value={percentage}
        className={cn('bg-muted', sizes[size], variants[variant])}
      />
    </div>
  )
}

export default ProgressBar
