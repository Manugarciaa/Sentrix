import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
  {
    variants: {
      variant: {
        default:
          'border-transparent bg-primary text-primary-foreground hover:bg-primary/80',
        secondary:
          'border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80',
        destructive:
          'border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80',
        outline: 'text-foreground',
        success:
          'border-transparent bg-primary-600 text-white hover:bg-primary-700',
        warning:
          'border-transparent bg-warning-500 text-white hover:bg-warning-600',
        danger:
          'border-transparent bg-danger-500 text-white hover:bg-danger-600',
        // Risk level specific variants
        riskAlto:
          'border-transparent bg-danger-100 text-danger-800 border-danger-200',
        riskMedio:
          'border-transparent bg-warning-100 text-warning-800 border-warning-200',
        riskBajo:
          'border-transparent bg-primary-100 text-primary-800 border-primary-200',
        riskMinimo:
          'border-transparent bg-gray-100 text-gray-800 border-gray-200',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {
  icon?: React.ReactNode
  removable?: boolean
  onRemove?: () => void
}

function Badge({ className, variant, icon, removable, onRemove, children, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props}>
      {icon && <span className="mr-1">{icon}</span>}
      {children}
      {removable && (
        <button
          type="button"
          onClick={onRemove}
          className="ml-1 rounded-full hover:bg-black/10 p-0.5"
        >
          <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  )
}

// Helper function to get risk level badge variant
export function getRiskLevelBadge(riskLevel: string) {
  switch (riskLevel.toUpperCase()) {
    case 'ALTO':
      return 'riskAlto'
    case 'MEDIO':
      return 'riskMedio'
    case 'BAJO':
      return 'riskBajo'
    case 'MÍNIMO':
    case 'MINIMO':
      return 'riskMinimo'
    default:
      return 'default'
  }
}

export { Badge, badgeVariants }