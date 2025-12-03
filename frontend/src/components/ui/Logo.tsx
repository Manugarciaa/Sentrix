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
  const [isLoaded, setIsLoaded] = React.useState(false)

  // Use white logo (w) for dark theme, black logo (b) for light theme
  const logoSrc = theme === 'dark'
    ? '/images/Logo-Sentrix-w.png'
    : '/images/Logo-Sentrix-b.png'

  // Preload both logos on mount
  React.useEffect(() => {
    const darkLogo = new Image()
    const lightLogo = new Image()
    darkLogo.src = '/images/Logo-Sentrix-w.png'
    lightLogo.src = '/images/Logo-Sentrix-b.png'

    Promise.all([
      new Promise(resolve => { darkLogo.onload = resolve }),
      new Promise(resolve => { lightLogo.onload = resolve })
    ]).then(() => setIsLoaded(true))
  }, [])

  return (
    <img
      key={theme}
      src={logoSrc}
      alt={alt}
      className={cn(
        "transition-all duration-300",
        isLoaded ? "opacity-100" : "opacity-0",
        className
      )}
    />
  )
}