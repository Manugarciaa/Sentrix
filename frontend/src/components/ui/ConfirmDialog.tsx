import React from 'react'
import { AlertTriangle, Trash2, Info } from 'lucide-react'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { cn } from '@/lib/utils'

export interface ConfirmDialogProps {
  open: boolean
  onClose: () => void
  onConfirm: () => void | Promise<void>
  title: string
  description: string
  confirmText?: string
  cancelText?: string
  variant?: 'danger' | 'warning' | 'info'
  isLoading?: boolean
}

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  open,
  onClose,
  onConfirm,
  title,
  description,
  confirmText = 'Confirmar',
  cancelText = 'Cancelar',
  variant = 'warning',
  isLoading = false,
}) => {
  const getIcon = () => {
    switch (variant) {
      case 'danger':
        return <Trash2 className="h-6 w-6" />
      case 'warning':
        return <AlertTriangle className="h-6 w-6" />
      case 'info':
        return <Info className="h-6 w-6" />
    }
  }

  const getIconStyles = () => {
    switch (variant) {
      case 'danger':
        return 'bg-red-100 text-red-600 dark:bg-red-950 dark:text-red-400'
      case 'warning':
        return 'bg-amber-100 text-amber-600 dark:bg-amber-950 dark:text-amber-400'
      case 'info':
        return 'bg-blue-100 text-blue-600 dark:bg-blue-950 dark:text-blue-400'
    }
  }

  const getButtonVariant = () => {
    switch (variant) {
      case 'danger':
        return 'destructive'
      case 'warning':
        return 'default'
      case 'info':
        return 'default'
    }
  }

  const handleConfirm = async () => {
    await onConfirm()
    if (!isLoading) {
      onClose()
    }
  }

  return (
    <AlertDialog open={open} onOpenChange={onClose}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <div className="flex items-start gap-4">
            {/* Icon */}
            <div
              className={cn(
                'shrink-0 w-12 h-12 rounded-full flex items-center justify-center',
                getIconStyles()
              )}
            >
              {getIcon()}
            </div>

            {/* Content */}
            <div className="flex-1 pt-1">
              <AlertDialogTitle className="text-lg font-bold mb-2">{title}</AlertDialogTitle>
              <AlertDialogDescription className="text-sm leading-relaxed">
                {description}
              </AlertDialogDescription>
            </div>
          </div>
        </AlertDialogHeader>

        <AlertDialogFooter>
          <AlertDialogCancel onClick={onClose} disabled={isLoading}>
            {cancelText}
          </AlertDialogCancel>
          <AlertDialogAction
            onClick={handleConfirm}
            disabled={isLoading}
            className={cn(
              getButtonVariant() === 'destructive' &&
                'bg-destructive text-destructive-foreground hover:bg-destructive/90'
            )}
          >
            {isLoading ? 'Procesando...' : confirmText}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}

// Hook for easier usage
export const useConfirmDialog = () => {
  const [dialogState, setDialogState] = React.useState<{
    open: boolean
    title: string
    description: string
    onConfirm: () => void | Promise<void>
    variant?: 'danger' | 'warning' | 'info'
    confirmText?: string
  }>({
    open: false,
    title: '',
    description: '',
    onConfirm: () => {},
  })

  const confirm = (options: Omit<typeof dialogState, 'open'>) => {
    return new Promise<boolean>((resolve) => {
      setDialogState({
        ...options,
        open: true,
      })
    })
  }

  const handleConfirm = async () => {
    await dialogState.onConfirm()
    setDialogState((prev) => ({ ...prev, open: false }))
  }

  const handleClose = () => {
    setDialogState((prev) => ({ ...prev, open: false }))
  }

  const dialog = (
    <ConfirmDialog
      open={dialogState.open}
      onClose={handleClose}
      onConfirm={handleConfirm}
      title={dialogState.title}
      description={dialogState.description}
      variant={dialogState.variant}
      confirmText={dialogState.confirmText}
    />
  )

  return { confirm, dialog }
}

export default ConfirmDialog
