/**
 * Toast Notification Helper
 *
 * Unified interface for toast notifications using Sonner library.
 * This helper provides a consistent API across the application and makes it easy
 * to add custom behavior or styling in the future.
 *
 * Usage:
 * ```typescript
 * import { showToast } from '@/lib/toast'
 *
 * showToast.success('Success!', 'Operation completed')
 * showToast.error('Error!', 'Something went wrong')
 * showToast.warning('Warning!', 'Please be careful')
 * showToast.info('Info', 'Just so you know')
 * ```
 */

import type { ComponentProps } from 'react'
import { toast as sonnerToast, Toaster as SonnerToaster } from 'sonner'

export interface ToastOptions {
  description?: string
  duration?: number
  action?: {
    label: string
    onClick: () => void
  }
  onDismiss?: () => void
  onAutoClose?: () => void
  position?: 'top-left' | 'top-center' | 'top-right' | 'bottom-left' | 'bottom-center' | 'bottom-right'
}

/**
 * Show a success toast notification
 * All toasts appear at top-right for consistency
 */
const success = (title: string, description?: string, options?: ToastOptions) => {
  const duration = options?.duration || 5000
  return sonnerToast.success(title, {
    description,
    duration,
    action: options?.action,
    onDismiss: options?.onDismiss,
    onAutoClose: options?.onAutoClose,
    position: options?.position || 'top-right',
    closeButton: duration > 7000, // Solo mostrar X si la duración es mayor a 7 segundos
  })
}

/**
 * Show an error toast notification
 * All toasts appear at top-right for consistency
 */
const error = (title: string, description?: string, options?: ToastOptions) => {
  const duration = options?.duration || 6000
  return sonnerToast.error(title, {
    description,
    duration,
    action: options?.action,
    onDismiss: options?.onDismiss,
    onAutoClose: options?.onAutoClose,
    position: options?.position || 'top-right',
    closeButton: duration > 7000, // Solo mostrar X si la duración es mayor a 7 segundos
  })
}

/**
 * Show a warning toast notification
 * All toasts appear at top-right for consistency
 */
const warning = (title: string, description?: string, options?: ToastOptions) => {
  const duration = options?.duration || 6000
  return sonnerToast.warning(title, {
    description,
    duration,
    action: options?.action,
    onDismiss: options?.onDismiss,
    onAutoClose: options?.onAutoClose,
    position: options?.position || 'top-right',
    closeButton: duration > 7000, // Solo mostrar X si la duración es mayor a 7 segundos
  })
}

/**
 * Show an info toast notification
 * All toasts appear at top-right for consistency
 */
const info = (title: string, description?: string, options?: ToastOptions) => {
  const duration = options?.duration || 5000
  return sonnerToast.info(title, {
    description,
    duration,
    action: options?.action,
    onDismiss: options?.onDismiss,
    onAutoClose: options?.onAutoClose,
    position: options?.position || 'top-right',
    closeButton: duration > 7000, // Solo mostrar X si la duración es mayor a 7 segundos
  })
}

/**
 * Show a promise toast notification (for async operations)
 */
const promise = <T,>(
  promise: Promise<T>,
  options: {
    loading: string
    success: string | ((data: T) => string)
    error: string | ((error: any) => string)
    description?: string
  }
) => {
  return sonnerToast.promise(promise, {
    loading: options.loading,
    success: options.success,
    error: options.error,
    description: options.description,
  })
}

/**
 * Dismiss a specific toast by ID
 */
const dismiss = (toastId?: string | number) => {
  sonnerToast.dismiss(toastId)
}

/**
 * Dismiss all active toasts
 */
const dismissAll = () => {
  sonnerToast.dismiss()
}

/**
 * Main toast object with all methods
 */
export const showToast = {
  success,
  error,
  warning,
  info,
  promise,
  dismiss,
  dismissAll,
}

/**
 * Legacy compatibility: Maps old addNotification format to new toast format
 * Use this for gradual migration from the old system
 *
 * @deprecated Use showToast directly instead
 */
export const notificationToToast = (notification: {
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
  duration?: number
}) => {
  const { type, title, message, duration } = notification

  switch (type) {
    case 'success':
      return showToast.success(title, message, { duration })
    case 'error':
      return showToast.error(title, message, { duration })
    case 'warning':
      return showToast.warning(title, message, { duration })
    case 'info':
      return showToast.info(title, message, { duration })
    default:
      return showToast.info(title, message, { duration })
  }
}

// Re-export sonner toast for advanced usage
export { sonnerToast as toast }
export { SonnerToaster }
export type SonnerToasterProps = ComponentProps<typeof SonnerToaster>
