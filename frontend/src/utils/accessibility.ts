/**
 * Accessibility utilities for Sentrix application
 */

/**
 * Generates accessible ARIA labels for common UI elements
 */
export const ariaLabels = {
  navigation: {
    main: 'Navegación principal',
    user: 'Menú de usuario',
    breadcrumb: 'Ruta de navegación',
    pagination: 'Paginación de resultados',
  },
  actions: {
    search: 'Buscar',
    filter: 'Filtrar resultados',
    sort: 'Ordenar',
    refresh: 'Actualizar',
    download: 'Descargar',
    upload: 'Subir archivo',
    delete: 'Eliminar',
    edit: 'Editar',
    save: 'Guardar',
    cancel: 'Cancelar',
    close: 'Cerrar',
    expand: 'Expandir',
    collapse: 'Contraer',
  },
  status: {
    loading: 'Cargando...',
    error: 'Error',
    success: 'Operación exitosa',
    warning: 'Advertencia',
  },
}

/**
 * Creates descriptive ARIA label for detection status
 */
export function getDetectionAriaLabel(
  confidence: number,
  validated: boolean,
  riskLevel?: string
): string {
  const confidencePercent = Math.round(confidence * 100)
  const validationText = validated ? 'validada' : 'pendiente de validación'
  const riskText = riskLevel ? `, nivel de riesgo ${riskLevel}` : ''

  return `Detección con ${confidencePercent}% de confianza, ${validationText}${riskText}`
}

/**
 * Creates descriptive ARIA label for analysis status
 */
export function getAnalysisAriaLabel(
  detectionCount: number,
  date: string,
  location?: string
): string {
  const locationText = location ? ` en ${location}` : ''
  return `Análisis del ${date} con ${detectionCount} detección${
    detectionCount !== 1 ? 'es' : ''
  }${locationText}`
}

/**
 * Announces screen reader messages dynamically
 */
export function announceToScreenReader(message: string, priority: 'polite' | 'assertive' = 'polite') {
  const announcement = document.createElement('div')
  announcement.setAttribute('role', 'status')
  announcement.setAttribute('aria-live', priority)
  announcement.setAttribute('aria-atomic', 'true')
  announcement.className = 'sr-only'
  announcement.textContent = message

  document.body.appendChild(announcement)

  // Remove after announcement
  setTimeout(() => {
    document.body.removeChild(announcement)
  }, 1000)
}

/**
 * Trap focus within a modal or dialog
 */
export function trapFocus(element: HTMLElement) {
  const focusableElements = element.querySelectorAll<HTMLElement>(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  )

  const firstFocusable = focusableElements[0]
  const lastFocusable = focusableElements[focusableElements.length - 1]

  function handleTabKey(e: KeyboardEvent) {
    if (e.key !== 'Tab') return

    if (e.shiftKey) {
      // Shift + Tab
      if (document.activeElement === firstFocusable) {
        e.preventDefault()
        lastFocusable?.focus()
      }
    } else {
      // Tab
      if (document.activeElement === lastFocusable) {
        e.preventDefault()
        firstFocusable?.focus()
      }
    }
  }

  element.addEventListener('keydown', handleTabKey)

  // Focus first element
  firstFocusable?.focus()

  // Return cleanup function
  return () => {
    element.removeEventListener('keydown', handleTabKey)
  }
}

/**
 * Handle escape key to close modals/dialogs
 */
export function useEscapeKey(callback: () => void) {
  function handleEscape(e: KeyboardEvent) {
    if (e.key === 'Escape') {
      callback()
    }
  }

  document.addEventListener('keydown', handleEscape)

  return () => {
    document.removeEventListener('keydown', handleEscape)
  }
}

/**
 * Get color contrast ratio (WCAG AA requires 4.5:1 for normal text)
 */
export function getContrastRatio(foreground: string, background: string): number {
  const getLuminance = (hex: string): number => {
    const rgb = parseInt(hex.slice(1), 16)
    const r = (rgb >> 16) & 0xff
    const g = (rgb >> 8) & 0xff
    const b = (rgb >> 0) & 0xff

    const [rs, gs, bs] = [r, g, b].map((c) => {
      const s = c / 255
      return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4)
    })

    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs
  }

  const l1 = getLuminance(foreground)
  const l2 = getLuminance(background)

  const lighter = Math.max(l1, l2)
  const darker = Math.min(l1, l2)

  return (lighter + 0.05) / (darker + 0.05)
}

/**
 * Check if color combination meets WCAG accessibility standards
 */
export function meetsContrastRequirements(
  foreground: string,
  background: string,
  level: 'AA' | 'AAA' = 'AA'
): { normal: boolean; large: boolean } {
  const ratio = getContrastRatio(foreground, background)

  if (level === 'AAA') {
    return {
      normal: ratio >= 7,
      large: ratio >= 4.5,
    }
  }

  return {
    normal: ratio >= 4.5,
    large: ratio >= 3,
  }
}

/**
 * Generate skip link for keyboard navigation
 */
export function createSkipLink(targetId: string, label: string = 'Saltar al contenido principal') {
  const skipLink = document.createElement('a')
  skipLink.href = `#${targetId}`
  skipLink.textContent = label
  skipLink.className =
    'sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary-600 focus:text-white focus:rounded'

  return skipLink
}

/**
 * Format number for screen readers (e.g., "1000" -> "mil")
 */
export function formatNumberForScreenReader(num: number): string {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)} millones`
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)} mil`
  }
  return num.toString()
}

/**
 * Format date for screen readers
 */
export function formatDateForScreenReader(date: Date): string {
  return date.toLocaleDateString('es-ES', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

export default {
  ariaLabels,
  getDetectionAriaLabel,
  getAnalysisAriaLabel,
  announceToScreenReader,
  trapFocus,
  useEscapeKey,
  getContrastRatio,
  meetsContrastRequirements,
  createSkipLink,
  formatNumberForScreenReader,
  formatDateForScreenReader,
}
