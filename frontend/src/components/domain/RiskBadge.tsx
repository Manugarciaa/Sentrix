import React from 'react'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/Badge'

export type RiskLevel = 'ALTO' | 'MEDIO' | 'BAJO' | 'MINIMO' | 'CRITICO'

export interface RiskBadgeProps {
  level: RiskLevel
  className?: string
  size?: 'sm' | 'md' | 'lg'
  showDot?: boolean
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({
  level,
  className,
  size = 'md',
  showDot = false,
}) => {
  const getRiskConfig = () => {
    switch (level) {
      case 'CRITICO':
        return {
          label: 'Crítico',
          variant: 'danger' as const,
          color: 'bg-red-100 text-red-700',
        }
      case 'ALTO':
        return {
          label: 'Alto',
          variant: 'danger' as const,
          color: 'bg-orange-100 text-orange-700',
        }
      case 'MEDIO':
        return {
          label: 'Medio',
          variant: 'warning' as const,
          color: 'bg-yellow-100 text-yellow-700',
        }
      case 'BAJO':
        return {
          label: 'Bajo',
          variant: 'success' as const,
          color: 'bg-green-100 text-green-700',
        }
      case 'MINIMO':
        return {
          label: 'Mínimo',
          variant: 'success' as const,
          color: 'bg-blue-100 text-blue-700',
        }
      default:
        return {
          label: level,
          variant: 'default' as const,
          color: 'bg-gray-100 text-gray-700',
        }
    }
  }

  const config = getRiskConfig()

  return (
    <Badge
      variant={config.variant}
      size={size}
      dot={showDot}
      className={cn(config.color, className)}
    >
      {config.label}
    </Badge>
  )
}

export default RiskBadge
