import React from 'react'
import { AlertTriangle, Trash2, AlertCircle, Info } from 'lucide-react'
import { Dialog, DialogHeader, DialogContent, DialogFooter } from '@/components/ui/Dialog'
import { Button } from '@/components/ui/Button'
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
        return 'bg-red-100 text-red-600'
      case 'warning':
        return 'bg-amber-100 text-amber-600'
      case 'info':
        return 'bg-blue-100 text-blue-600'
    }
  }

  const getButtonVariant = () => {
    switch (variant) {
      case 'danger':
        return 'destructive'
      case 'warning':
        return 'primary'
      case 'info':
        return 'primary'
    }
  }

  const handleConfirm = async () => {
    await onConfirm()
    if (!isLoading) {
      onClose()
    }
  }

  return (
    <Dialog open={open} onClose={onClose} size="sm">
      <DialogContent>
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
            <h3 className="text-lg font-bold text-gray-900 mb-2">{title}</h3>
            <p className="text-sm text-gray-600 leading-relaxed">{description}</p>
          </div>
        </div>
      </DialogContent>

      <DialogFooter>
        <Button onClick={onClose} variant="outline" disabled={isLoading}>
          {cancelText}
        </Button>
        <Button
          onClick={handleConfirm}
          variant={getButtonVariant()}
          disabled={isLoading}
        >
          {isLoading ? 'Procesando...' : confirmText}
        </Button>
      </DialogFooter>
    </Dialog>
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
