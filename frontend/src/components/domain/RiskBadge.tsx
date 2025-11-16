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
        }
      case 'ALTO':
        return {
          label: 'Alto',
          variant: 'danger' as const,
          customColor: 'bg-orange-100 dark:bg-orange-950/30 text-orange-700 dark:text-orange-400 border-orange-200 dark:border-orange-800/50',
        }
      case 'MEDIO':
        return {
          label: 'Medio',
          variant: 'warning' as const,
        }
      case 'BAJO':
        return {
          label: 'Bajo',
          variant: 'success' as const,
        }
      case 'MINIMO':
        return {
          label: 'Mínimo',
          variant: 'info' as const,
        }
      default:
        return {
          label: level,
          variant: 'default' as const,
        }
    }
  }

  const config = getRiskConfig()

  return (
    <Badge
      variant={config.variant}
      size={size}
      dot={showDot}
      className={cn(config.customColor, className)}
    >
      {config.label}
    </Badge>
  )
}

export default RiskBadge
