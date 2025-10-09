import React from 'react'
import { User } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface AvatarProps {
  src?: string
  alt?: string
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl'
  fallback?: string
  className?: string
}

export const Avatar: React.FC<AvatarProps> = ({
  src,
  alt = 'Avatar',
  size = 'md',
  fallback,
  className,
}) => {
  const [imageError, setImageError] = React.useState(false)

  const sizes = {
    xs: 'h-6 w-6',
    sm: 'h-8 w-8',
    md: 'h-10 w-10',
    lg: 'h-12 w-12',
    xl: 'h-16 w-16',
    '2xl': 'h-24 w-24',
  }

  const iconSizes = {
    xs: 'h-3 w-3',
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-6 w-6',
    xl: 'h-8 w-8',
    '2xl': 'h-12 w-12',
  }

  const textSizes = {
    xs: 'text-xs',
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg',
    xl: 'text-xl',
    '2xl': 'text-3xl',
  }

  const showFallback = !src || imageError

  return (
    <div
      className={cn(
        'relative inline-flex items-center justify-center rounded-full bg-gradient-to-br from-primary-600 to-cyan-600 overflow-hidden shrink-0',
        sizes[size],
        className
      )}
    >
      {!showFallback && src ? (
        <img
          src={src}
          alt={alt}
          className="h-full w-full object-cover"
          onError={() => setImageError(true)}
        />
      ) : fallback ? (
        <span className={cn('font-medium text-white', textSizes[size])}>
          {fallback}
        </span>
      ) : (
        <User className={cn('text-white', iconSizes[size])} />
      )}
    </div>
  )
}

export default Avatar
