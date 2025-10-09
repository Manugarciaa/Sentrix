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
            className="w-48 h-48 mx-auto mb-6"
            viewBox="0 0 200 200"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <circle cx="80" cy="80" r="45" stroke="#E5E7EB" strokeWidth="8" />
            <path
              d="M115 115L140 140"
              stroke="#E5E7EB"
              strokeWidth="8"
              strokeLinecap="round"
            />
            <circle cx="80" cy="80" r="20" fill="#F3F4F6" />
          </svg>
        )
      case 'upload':
        return (
          <svg
            className="w-48 h-48 mx-auto mb-6"
            viewBox="0 0 200 200"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <rect x="50" y="70" width="100" height="80" rx="8" fill="#F3F4F6" />
            <path
              d="M100 100V130M100 100L90 110M100 100L110 110"
              stroke="#9CA3AF"
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
              stroke="#E5E7EB"
              strokeWidth="3"
              strokeDasharray="8 8"
            />
          </svg>
        )
      case 'data':
        return (
          <svg
            className="w-48 h-48 mx-auto mb-6"
            viewBox="0 0 200 200"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <rect x="40" y="50" width="30" height="100" rx="4" fill="#F3F4F6" />
            <rect x="85" y="80" width="30" height="70" rx="4" fill="#E5E7EB" />
            <rect x="130" y="65" width="30" height="85" rx="4" fill="#F3F4F6" />
            <line
              x1="40"
              y1="160"
              x2="160"
              y2="160"
              stroke="#E5E7EB"
              strokeWidth="2"
            />
          </svg>
        )
    }
  }

  const getVariantStyles = () => {
    switch (variant) {
      case 'subtle':
        return 'bg-gray-50 rounded-lg border border-gray-200'
      case 'gradient':
        return 'bg-gradient-to-br from-primary-50 to-cyan-50 rounded-lg border border-primary-100'
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
        <div className="mb-6 rounded-full bg-gradient-to-br from-gray-100 to-gray-200 p-6 shadow-sm">
          <Icon className="h-12 w-12 text-gray-400" />
        </div>
      )}

      <h3 className="text-xl font-bold text-gray-900 mb-2">{title}</h3>

      {description && (
        <p className="text-base text-gray-600 max-w-md mb-6 leading-relaxed">
          {description}
        </p>
      )}

      {action && <div className="mt-2">{action}</div>}
    </div>
  )
}

export default EmptyState
