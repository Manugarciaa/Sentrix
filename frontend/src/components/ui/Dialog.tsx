import React, { useEffect } from 'react'
import { X } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface DialogProps {
  open: boolean
  onClose: () => void
  children: React.ReactNode
  className?: string
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
}

export const Dialog: React.FC<DialogProps> = ({
  open,
  onClose,
  children,
  className,
  size = 'md',
}) => {
  // Close on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && open) {
        onClose()
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [open, onClose])

  // Prevent body scroll when dialog is open
  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }

    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [open])

  if (!open) return null

  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-7xl',
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Dialog */}
      <div
        className={cn(
          'relative w-full bg-white rounded-2xl shadow-2xl',
          'max-h-[90vh] overflow-y-auto',
          'animate-in fade-in-0 zoom-in-95 duration-200',
          sizes[size],
          className
        )}
        role="dialog"
        aria-modal="true"
      >
        {children}
      </div>
    </div>
  )
}

export interface DialogHeaderProps {
  children: React.ReactNode
  className?: string
  onClose?: () => void
}

export const DialogHeader: React.FC<DialogHeaderProps> = ({
  children,
  className,
  onClose,
}) => {
  return (
    <div
      className={cn(
        'flex items-start justify-between p-6 border-b border-gray-200',
        className
      )}
    >
      <div className="flex-1">{children}</div>
      {onClose && (
        <button
          onClick={onClose}
          className="ml-4 p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
          aria-label="Close dialog"
        >
          <X className="h-5 w-5" />
        </button>
      )}
    </div>
  )
}

export interface DialogContentProps {
  children: React.ReactNode
  className?: string
}

export const DialogContent: React.FC<DialogContentProps> = ({
  children,
  className,
}) => {
  return <div className={cn('p-6', className)}>{children}</div>
}

export interface DialogFooterProps {
  children: React.ReactNode
  className?: string
}

export const DialogFooter: React.FC<DialogFooterProps> = ({
  children,
  className,
}) => {
  return (
    <div
      className={cn(
        'flex items-center justify-end gap-3 p-6 border-t border-gray-200',
        className
      )}
    >
      {children}
    </div>
  )
}

export interface DialogTitleProps {
  children: React.ReactNode
  className?: string
}

export const DialogTitle: React.FC<DialogTitleProps> = ({
  children,
  className,
}) => {
  return (
    <h3 className={cn('text-xl font-bold text-gray-900', className)}>
      {children}
    </h3>
  )
}

export interface DialogDescriptionProps {
  children: React.ReactNode
  className?: string
}

export const DialogDescription: React.FC<DialogDescriptionProps> = ({
  children,
  className,
}) => {
  return (
    <p className={cn('text-sm text-gray-600 mt-1', className)}>{children}</p>
  )
}

export default Dialog
