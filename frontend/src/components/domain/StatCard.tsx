import React from 'react'
import { LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface StatCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: LucideIcon
  gradient: string
  trend?: {
    value: number
    direction: 'up' | 'down' | 'neutral'
  }
  className?: string
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  gradient,
  trend,
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
        return 'text-green-100'
      case 'down':
        return 'text-red-100'
      case 'neutral':
        return 'text-white/70'
    }
  }

  return (
    <div
      className={cn(
        'relative rounded-xl p-6 text-white overflow-hidden shadow-lg transition-all duration-300',
        'hover:shadow-xl hover:-translate-y-1',
        gradient,
        className
      )}
    >
      {/* Background Icon */}
      <div className="absolute top-0 right-0 opacity-10">
        <Icon className="h-32 w-32" />
      </div>

      {/* Content */}
      <div className="relative">
        <p className="text-sm font-medium opacity-90 mb-2">
          {title}
        </p>

        <p className="text-4xl font-bold mb-1">
          {typeof value === 'number' ? value.toLocaleString() : value}
        </p>

        {subtitle && (
          <p className="text-sm opacity-80 mt-4">
            {subtitle}
          </p>
        )}

        {trend && (
          <div className={cn('flex items-center gap-1 mt-4 text-sm font-medium', getTrendColor())}>
            {getTrendIcon()}
            <span>
              {trend.value > 0 ? '+' : ''}{trend.value}% vs mes anterior
            </span>
          </div>
        )}
      </div>
    </div>
  )
}

export default StatCard
