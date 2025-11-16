import React from 'react'
import { useTheme } from '@/hooks/useTheme'
import { cn } from '@/lib/utils'

interface LogoProps {
  className?: string
  alt?: string
}

export const Logo: React.FC<LogoProps> = ({
  className = "h-14",
  alt = "Sentrix"
}) => {
  const { theme } = useTheme()

  // Use white logo (w) for dark theme, black logo (b) for light theme
  const logoSrc = theme === 'dark'
    ? '/images/Logo-Sentrix-w.png'
    : '/images/Logo-Sentrix-b.png'

  return (
    <img
      src={logoSrc}
      alt={alt}
      className={cn("transition-opacity duration-200", className)}
    />
  )
}