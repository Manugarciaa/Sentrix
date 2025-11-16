import React from 'react'
import { Moon, Sun } from 'lucide-react'
import { useTheme } from '@/hooks/useTheme'
import { cn } from '@/lib/utils'

interface ThemeToggleProps {
  className?: string
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ className }) => {
  const { theme, toggleTheme } = useTheme()

  return (
    <button
      onClick={toggleTheme}
      className={cn(
        'relative inline-flex h-9 w-9 items-center justify-center rounded-lg',
        'border border-border bg-background',
        'transition-all duration-200 ease-out',
        'hover:bg-accent hover:text-accent-foreground',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
        className
      )}
      aria-label={theme === 'light' ? 'Activar modo oscuro' : 'Activar modo claro'}
    >
      <Sun
        className={cn(
          'h-[1.2rem] w-[1.2rem] transition-all duration-300',
          theme === 'dark' ? 'rotate-90 scale-0 opacity-0' : 'rotate-0 scale-100 opacity-100'
        )}
      />
      <Moon
        className={cn(
          'absolute h-[1.2rem] w-[1.2rem] transition-all duration-300',
          theme === 'light' ? '-rotate-90 scale-0 opacity-0' : 'rotate-0 scale-100 opacity-100'
        )}
      />
      <span className="sr-only">Toggle theme</span>
    </button>
  )
}

export default ThemeToggle
