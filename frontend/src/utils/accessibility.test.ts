import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import {
  getDetectionAriaLabel,
  getAnalysisAriaLabel,
  announceToScreenReader,
  trapFocus,
  useEscapeKey,
  getContrastRatio,
  meetsContrastRequirements,
  formatNumberForScreenReader,
  formatDateForScreenReader,
} from './accessibility'

describe('Accessibility Utils', () => {
  describe('getDetectionAriaLabel', () => {
    it('generates correct label for unvalidated detection', () => {
      const label = getDetectionAriaLabel(0.85, false, 'high')
      expect(label).toBe(
        'Detección con 85% de confianza, pendiente de validación, nivel de riesgo high'
      )
    })

    it('generates correct label for validated detection', () => {
      const label = getDetectionAriaLabel(0.72, true)
      expect(label).toBe('Detección con 72% de confianza, validada')
    })
  })

  describe('getAnalysisAriaLabel', () => {
    it('generates label with location', () => {
      const label = getAnalysisAriaLabel(5, '2024-01-15', 'Buenos Aires')
      expect(label).toBe('Análisis del 2024-01-15 con 5 detecciones en Buenos Aires')
    })

    it('generates label without location', () => {
      const label = getAnalysisAriaLabel(1, '2024-01-15')
      expect(label).toBe('Análisis del 2024-01-15 con 1 detección')
    })

    it('uses singular for one detection', () => {
      const label = getAnalysisAriaLabel(1, '2024-01-15')
      expect(label).toContain('1 detección')
    })
  })

  describe('announceToScreenReader', () => {
    beforeEach(() => {
      vi.useFakeTimers()
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('creates announcement element', () => {
      announceToScreenReader('Test message')

      const announcement = document.querySelector('[role="status"]')
      expect(announcement).toBeInTheDocument()
      expect(announcement?.textContent).toBe('Test message')
    })

    it('removes announcement after timeout', () => {
      announceToScreenReader('Test message')

      vi.advanceTimersByTime(1000)

      const announcement = document.querySelector('[role="status"]')
      expect(announcement).not.toBeInTheDocument()
    })

    it('sets correct aria-live priority', () => {
      announceToScreenReader('Urgent!', 'assertive')

      const announcement = document.querySelector('[role="status"]')
      expect(announcement?.getAttribute('aria-live')).toBe('assertive')
    })
  })

  describe('trapFocus', () => {
    it('focuses first focusable element', () => {
      const container = document.createElement('div')
      const button1 = document.createElement('button')
      const button2 = document.createElement('button')
      container.appendChild(button1)
      container.appendChild(button2)
      document.body.appendChild(container)

      const focusSpy = vi.spyOn(button1, 'focus')

      trapFocus(container)

      expect(focusSpy).toHaveBeenCalled()

      document.body.removeChild(container)
    })

    it('returns cleanup function', () => {
      const container = document.createElement('div')
      const button = document.createElement('button')
      container.appendChild(button)
      document.body.appendChild(container)

      const cleanup = trapFocus(container)

      expect(typeof cleanup).toBe('function')
      cleanup()

      document.body.removeChild(container)
    })
  })

  describe('useEscapeKey', () => {
    it('calls callback on Escape key', () => {
      const callback = vi.fn()
      const cleanup = useEscapeKey(callback)

      const event = new KeyboardEvent('keydown', { key: 'Escape' })
      document.dispatchEvent(event)

      expect(callback).toHaveBeenCalled()

      cleanup()
    })

    it('does not call callback on other keys', () => {
      const callback = vi.fn()
      const cleanup = useEscapeKey(callback)

      const event = new KeyboardEvent('keydown', { key: 'Enter' })
      document.dispatchEvent(event)

      expect(callback).not.toHaveBeenCalled()

      cleanup()
    })
  })

  describe('getContrastRatio', () => {
    it('calculates contrast ratio correctly', () => {
      // Black on white should have maximum contrast
      const ratio = getContrastRatio('#000000', '#FFFFFF')
      expect(ratio).toBeCloseTo(21, 0)
    })

    it('returns 1 for same colors', () => {
      const ratio = getContrastRatio('#FFFFFF', '#FFFFFF')
      expect(ratio).toBeCloseTo(1, 0)
    })
  })

  describe('meetsContrastRequirements', () => {
    it('passes AA requirements for black on white', () => {
      const result = meetsContrastRequirements('#000000', '#FFFFFF', 'AA')
      expect(result.normal).toBe(true)
      expect(result.large).toBe(true)
    })

    it('fails for low contrast', () => {
      const result = meetsContrastRequirements('#888888', '#999999', 'AA')
      expect(result.normal).toBe(false)
      expect(result.large).toBe(false)
    })

    it('checks AAA requirements', () => {
      const result = meetsContrastRequirements('#000000', '#FFFFFF', 'AAA')
      expect(result.normal).toBe(true)
      expect(result.large).toBe(true)
    })
  })

  describe('formatNumberForScreenReader', () => {
    it('formats large numbers correctly', () => {
      expect(formatNumberForScreenReader(1500000)).toBe('1.5 millones')
      expect(formatNumberForScreenReader(2500)).toBe('2.5 mil')
      expect(formatNumberForScreenReader(999)).toBe('999')
    })
  })

  describe('formatDateForScreenReader', () => {
    it('formats date in Spanish', () => {
      const date = new Date('2024-01-15')
      const formatted = formatDateForScreenReader(date)
      expect(formatted).toContain('2024')
      expect(formatted).toContain('enero')
    })
  })
})
