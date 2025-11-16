import React, { useState } from 'react'
import { CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import { Dialog, DialogHeader, DialogContent, DialogFooter } from '@/components/ui/Dialog'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { RiskBadge } from './RiskBadge'
import type { Detection } from '@/types'

export interface ValidationModalProps {
  open: boolean
  onClose: () => void
  detection: Detection | null
  onValidate: (detectionId: string, status: 'validated_positive' | 'validated_negative', notes?: string) => Promise<void>
  isLoading?: boolean
}

export const ValidationModal: React.FC<ValidationModalProps> = ({
  open,
  onClose,
  detection,
  onValidate,
  isLoading = false,
}) => {
  const [validationStatus, setValidationStatus] = useState<'validated_positive' | 'validated_negative' | null>(null)
  const [notes, setNotes] = useState('')
  const [error, setError] = useState('')

  const handleClose = () => {
    setValidationStatus(null)
    setNotes('')
    setError('')
    onClose()
  }

  const handleSubmit = async () => {
    if (!detection || !validationStatus) {
      setError('Por favor selecciona una opción de validación')
      return
    }

    try {
      setError('')
      await onValidate(detection.id, validationStatus, notes || undefined)
      handleClose()
    } catch (err) {
      setError('Error al validar la detección. Por favor intenta nuevamente.')
      console.error('Validation error:', err)
    }
  }

  if (!detection) return null

  return (
    <Dialog open={open} onClose={handleClose} size="md">
      <DialogHeader>
        <h3 className="text-xl font-bold text-gray-900">Validar Detección</h3>
        <p className="text-sm text-gray-600 mt-1">
          Confirma o rechaza esta detección de criadero
        </p>
      </DialogHeader>

      <DialogContent>
        {/* Detection Info */}
        <div className="bg-gray-50 rounded-lg p-4 mb-4">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h4 className="font-semibold text-gray-900">
                {detection.breeding_site_type || detection.class_name}
              </h4>
              <p className="text-xs text-gray-600 mt-1">
                ID: {detection.id.slice(0, 16)}...
              </p>
            </div>
            <RiskBadge level={detection.risk_level} />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <p className="text-xs text-gray-600">Confianza</p>
              <p className="text-lg font-bold text-gray-900">
                {(detection.confidence * 100).toFixed(1)}%
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-600">Área</p>
              <p className="text-lg font-bold text-gray-900">
                {detection.mask_area?.toFixed(0) || detection.area_square_pixels?.toFixed(0) || 'N/A'} px²
              </p>
            </div>
          </div>

          {detection.location?.has_location && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <p className="text-xs text-gray-600">Ubicación</p>
              <p className="text-sm text-gray-900">
                {detection.location.latitude?.toFixed(6)}, {detection.location.longitude?.toFixed(6)}
              </p>
            </div>
          )}
        </div>

        {/* Validation Options */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Estado de Validación *
          </label>
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => setValidationStatus('validated_positive')}
              className={`p-4 rounded-lg border-2 transition-all ${
                validationStatus === 'validated_positive'
                  ? 'border-green-500 bg-green-50'
                  : 'border-gray-200 hover:border-green-300'
              }`}
            >
              <CheckCircle
                className={`h-8 w-8 mx-auto mb-2 ${
                  validationStatus === 'validated_positive' ? 'text-green-600' : 'text-gray-400'
                }`}
              />
              <p className="text-sm font-medium text-gray-900">Confirmar</p>
              <p className="text-xs text-gray-600">Es un criadero</p>
            </button>

            <button
              onClick={() => setValidationStatus('validated_negative')}
              className={`p-4 rounded-lg border-2 transition-all ${
                validationStatus === 'validated_negative'
                  ? 'border-red-500 bg-red-50'
                  : 'border-gray-200 hover:border-red-300'
              }`}
            >
              <XCircle
                className={`h-8 w-8 mx-auto mb-2 ${
                  validationStatus === 'validated_negative' ? 'text-red-600' : 'text-gray-400'
                }`}
              />
              <p className="text-sm font-medium text-gray-900">Rechazar</p>
              <p className="text-xs text-gray-600">No es un criadero</p>
            </button>
          </div>
        </div>

        {/* Notes */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            Notas (Opcional)
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Agrega comentarios sobre esta validación..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
            rows={3}
          />
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
            <AlertCircle className="h-5 w-5 text-red-600 shrink-0 mt-0.5" />
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}
      </DialogContent>

      <DialogFooter>
        <Button
          onClick={handleClose}
          variant="outline"
          disabled={isLoading}
        >
          Cancelar
        </Button>
        <Button
          onClick={handleSubmit}
          disabled={!validationStatus || isLoading}
          className="bg-gradient-to-r from-primary-600 to-cyan-600 hover:from-primary-700 hover:to-cyan-700"
        >
          {isLoading ? 'Validando...' : 'Validar Detección'}
        </Button>
      </DialogFooter>
    </Dialog>
  )
}

export default ValidationModal
