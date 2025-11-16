import React from 'react'
import { LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface StatCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: LucideIcon
  trend?: {
    value: number
    direction: 'up' | 'down' | 'neutral'
  }
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger'
  className?: string
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  variant = 'default',
  className,
}) => {
  const getTrendIcon = () => {
    if (!trend) return null

    switch (trend.direction) {
      case 'up':
        return <TrendingUp className="h-4 w-4" />
      case 'down':
        return <TrendingDown className="h-4 w-4" />
      case 'neutral':
        return <Minus className="h-4 w-4" />
    }
  }

  const getTrendColor = () => {
    if (!trend) return ''

    switch (trend.direction) {
      case 'up':
        return 'text-green-600 dark:text-green-400'
      case 'down':
        return 'text-red-600 dark:text-red-400'
      case 'neutral':
        return 'text-muted-foreground'
    }
  }

  const getVariantStyles = () => {
    switch (variant) {
      case 'primary':
        return 'bg-primary/5 dark:bg-primary/10 border-primary/20 dark:border-primary/30'
      case 'success':
        return 'bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-800/50'
      case 'warning':
        return 'bg-yellow-50 dark:bg-yellow-950/20 border-yellow-200 dark:border-yellow-800/50'
      case 'danger':
        return 'bg-red-50 dark:bg-red-950/20 border-red-200 dark:border-red-800/50'
      default:
        return 'bg-card border-border'
    }
  }

  const getIconStyles = () => {
    switch (variant) {
      case 'primary':
        return 'text-primary'
      case 'success':
        return 'text-green-600 dark:text-green-400'
      case 'warning':
        return 'text-yellow-600 dark:text-yellow-400'
      case 'danger':
        return 'text-red-600 dark:text-red-400'
      default:
        return 'text-muted-foreground'
    }
  }

  return (
    <div
      className={cn(
        'group relative rounded-xl p-6 border-2 overflow-hidden shadow-sm',
        'hover:shadow-md hover:-translate-y-1 transition-all duration-300',
        getVariantStyles(),
        className
      )}
    >
      {/* Background Icon */}
      <div className="absolute -top-4 -right-4 opacity-[0.03] dark:opacity-[0.05] transition-all duration-300 group-hover:opacity-[0.06] dark:group-hover:opacity-[0.08]">
        <Icon className="h-32 w-32" />
      </div>

      {/* Icon Badge */}
      <div className="relative mb-4">
        <div className={cn(
          'inline-flex p-3 rounded-xl transition-all duration-300',
          'bg-background/50 dark:bg-background/30 border border-border/50',
          'group-hover:scale-110 group-hover:shadow-md'
        )}>
          <Icon className={cn('h-5 w-5', getIconStyles())} />
        </div>
      </div>

      {/* Content */}
      <div className="relative space-y-1">
        <p className="text-sm font-medium text-muted-foreground">
          {title}
        </p>

        <p className="text-3xl sm:text-4xl font-bold text-foreground">
          {typeof value === 'number' ? value.toLocaleString() : value}
        </p>

        {subtitle && (
          <p className="text-sm text-muted-foreground pt-2">
            {subtitle}
          </p>
        )}

        {trend && (
          <div className={cn(
            'flex items-center gap-1.5 pt-3 text-sm font-medium',
            getTrendColor()
          )}>
            {getTrendIcon()}
            <span>
              {trend.value > 0 ? '+' : ''}{trend.value}% vs anterior
            </span>
          </div>
        )}
      </div>
    </div>
  )
}

export default StatCard
