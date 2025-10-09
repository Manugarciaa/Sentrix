import React from 'react'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/Badge'
import { Shield, Star, User } from 'lucide-react'

export type UserRole = 'ADMIN' | 'EXPERT' | 'USER'

export interface RoleBadgeProps {
  role: UserRole
  className?: string
  size?: 'sm' | 'md' | 'lg'
  showIcon?: boolean
}

export const RoleBadge: React.FC<RoleBadgeProps> = ({
  role,
  className,
  size = 'md',
  showIcon = false,
}) => {
  const getRoleConfig = () => {
    switch (role) {
      case 'ADMIN':
        return {
          label: 'Administrador',
          color: 'bg-purple-100 text-purple-700',
          icon: Shield,
        }
      case 'EXPERT':
        return {
          label: 'Experto',
          color: 'bg-blue-100 text-blue-700',
          icon: Star,
        }
      case 'USER':
        return {
          label: 'Usuario',
          color: 'bg-gray-100 text-gray-700',
          icon: User,
        }
      default:
        return {
          label: role,
          color: 'bg-gray-100 text-gray-700',
          icon: User,
        }
    }
  }

  const config = getRoleConfig()
  const Icon = config.icon

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-full',
        config.color,
        className
      )}
    >
      {showIcon && <Icon className="h-3 w-3" />}
      {config.label}
    </span>
  )
}

export default RoleBadge
