import React from 'react'
import { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description?: string
  action?: React.ReactNode
  className?: string
  variant?: 'default' | 'subtle' | 'gradient'
  illustration?: 'search' | 'upload' | 'data' | 'none'
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon: Icon,
  title,
  description,
  action,
  className,
  variant = 'default',
  illustration = 'none',
}) => {
  const getIllustration = () => {
    if (illustration === 'none') return null

    switch (illustration) {
      case 'search':
        return (
          <svg
            className="w-48 h-48 mx-auto mb-6 opacity-50 dark:opacity-30"
            viewBox="0 0 200 200"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <circle cx="80" cy="80" r="45" className="stroke-border" strokeWidth="8" />
            <path
              d="M115 115L140 140"
              className="stroke-border"
              strokeWidth="8"
              strokeLinecap="round"
            />
            <circle cx="80" cy="80" r="20" className="fill-muted" />
          </svg>
        )
      case 'upload':
        return (
          <svg
            className="w-48 h-48 mx-auto mb-6 opacity-50 dark:opacity-30"
            viewBox="0 0 200 200"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <rect x="50" y="70" width="100" height="80" rx="8" className="fill-muted" />
            <path
              d="M100 100V130M100 100L90 110M100 100L110 110"
              className="stroke-muted-foreground"
              strokeWidth="4"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <rect
              x="50"
              y="70"
              width="100"
              height="80"
              rx="8"
              className="stroke-border"
              strokeWidth="3"
              strokeDasharray="8 8"
            />
          </svg>
        )
      case 'data':
        return (
          <svg
            className="w-48 h-48 mx-auto mb-6 opacity-50 dark:opacity-30"
            viewBox="0 0 200 200"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <rect x="40" y="50" width="30" height="100" rx="4" className="fill-muted" />
            <rect x="85" y="80" width="30" height="70" rx="4" className="fill-border" />
            <rect x="130" y="65" width="30" height="85" rx="4" className="fill-muted" />
            <line
              x1="40"
              y1="160"
              x2="160"
              y2="160"
              className="stroke-border"
              strokeWidth="2"
            />
          </svg>
        )
    }
  }

  const getVariantStyles = () => {
    switch (variant) {
      case 'subtle':
        return 'bg-muted/30 dark:bg-muted/10 rounded-xl border-2 border-border'
      case 'gradient':
        return 'bg-primary/5 dark:bg-primary/10 rounded-xl border-2 border-primary/20 dark:border-primary/30'
      default:
        return ''
    }
  }

  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center py-12 px-4 text-center',
        getVariantStyles(),
        className
      )}
    >
      {illustration !== 'none' ? (
        getIllustration()
      ) : (
        <div className="mb-6 rounded-2xl bg-muted/50 dark:bg-muted/30 p-6 border-2 border-border shadow-sm">
          <Icon className="h-12 w-12 text-muted-foreground" />
        </div>
      )}

      <h3 className="text-xl font-bold text-foreground mb-2">{title}</h3>

      {description && (
        <p className="text-base text-muted-foreground max-w-md mb-6 leading-relaxed">
          {description}
        </p>
      )}

      {action && <div className="mt-2">{action}</div>}
    </div>
  )
}

export default EmptyState
