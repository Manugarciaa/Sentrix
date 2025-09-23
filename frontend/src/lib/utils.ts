import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: Date | string, options?: Intl.DateTimeFormatOptions) {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return new Intl.DateTimeFormat('es-ES', {
    dateStyle: 'medium',
    timeStyle: 'short',
    ...options,
  }).format(dateObj)
}

export function formatFileSize(bytes: number) {
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  if (bytes === 0) return '0 Bytes'
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

export function generateId() {
  return Math.random().toString(36).substr(2, 9)
}

export function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

export function sanitizeFilename(filename: string) {
  return filename.replace(/[^a-z0-9]/gi, '_').toLowerCase()
}

export function isValidEmail(email: string) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export function copyToClipboard(text: string) {
  return navigator.clipboard.writeText(text)
}

export function downloadFile(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

export function getRiskLevelColor(level: string) {
  switch (level.toUpperCase()) {
    case 'ALTO':
      return 'risk-level-alto'
    case 'MEDIO':
      return 'risk-level-medio'
    case 'BAJO':
      return 'risk-level-bajo'
    case 'MÍNIMO':
    case 'MINIMO':
      return 'risk-level-minimo'
    default:
      return 'risk-level-minimo'
  }
}

export function getRiskLevelText(level: string) {
  switch (level.toUpperCase()) {
    case 'ALTO':
      return 'Alto Riesgo'
    case 'MEDIO':
      return 'Riesgo Medio'
    case 'BAJO':
      return 'Riesgo Bajo'
    case 'MÍNIMO':
    case 'MINIMO':
      return 'Riesgo Mínimo'
    default:
      return 'Sin Clasificar'
  }
}