import React, { useState } from 'react'
import { Lock, AlertCircle, CheckCircle } from 'lucide-react'
import { Dialog, DialogHeader, DialogContent, DialogFooter } from '@/components/ui/Dialog'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'

export interface ChangePasswordModalProps {
  open: boolean
  onClose: () => void
  onSubmit: (currentPassword: string, newPassword: string) => Promise<void>
  isLoading?: boolean
}

export const ChangePasswordModal: React.FC<ChangePasswordModalProps> = ({
  open,
  onClose,
  onSubmit,
  isLoading = false,
}) => {
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [errors, setErrors] = useState<{
    currentPassword?: string
    newPassword?: string
    confirmPassword?: string
  }>({})

  const validateForm = (): boolean => {
    const newErrors: typeof errors = {}

    if (!currentPassword) {
      newErrors.currentPassword = 'La contraseña actual es requerida'
    }

    if (!newPassword) {
      newErrors.newPassword = 'La nueva contraseña es requerida'
    } else if (newPassword.length < 6) {
      newErrors.newPassword = 'La contraseña debe tener al menos 6 caracteres'
    }

    if (!confirmPassword) {
      newErrors.confirmPassword = 'Debes confirmar la nueva contraseña'
    } else if (newPassword !== confirmPassword) {
      newErrors.confirmPassword = 'Las contraseñas no coinciden'
    }

    if (currentPassword && newPassword && currentPassword === newPassword) {
      newErrors.newPassword = 'La nueva contraseña debe ser diferente a la actual'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async () => {
    if (!validateForm()) return

    try {
      await onSubmit(currentPassword, newPassword)
      handleClose()
    } catch (error) {
      console.error('Error changing password:', error)
      setErrors({
        currentPassword: 'Contraseña actual incorrecta',
      })
    }
  }

  const handleClose = () => {
    setCurrentPassword('')
    setNewPassword('')
    setConfirmPassword('')
    setErrors({})
    onClose()
  }

  const getPasswordStrength = (password: string): { level: number; label: string; color: string } => {
    if (!password) return { level: 0, label: '', color: '' }

    let strength = 0
    if (password.length >= 6) strength++
    if (password.length >= 8) strength++
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++
    if (/\d/.test(password)) strength++
    if (/[^a-zA-Z0-9]/.test(password)) strength++

    if (strength <= 2) return { level: strength, label: 'Débil', color: 'bg-red-500' }
    if (strength <= 3) return { level: strength, label: 'Media', color: 'bg-amber-500' }
    return { level: strength, label: 'Fuerte', color: 'bg-green-500' }
  }

  const passwordStrength = getPasswordStrength(newPassword)

  return (
    <Dialog open={open} onClose={handleClose} size="md">
      <DialogHeader>
        <h3 className="text-xl font-bold text-gray-900">Cambiar Contraseña</h3>
        <p className="text-sm text-gray-600 mt-1">
          Actualiza tu contraseña para mantener tu cuenta segura
        </p>
      </DialogHeader>

      <DialogContent>
        <div className="space-y-4">
          {/* Current Password */}
          <Input
            label="Contraseña actual"
            type="password"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            error={errors.currentPassword}
            placeholder="Ingresa tu contraseña actual"
            icon={Lock}
            required
          />

          {/* New Password */}
          <div>
            <Input
              label="Nueva contraseña"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              error={errors.newPassword}
              placeholder="Mínimo 6 caracteres"
              icon={Lock}
              required
            />

            {/* Password Strength Indicator */}
            {newPassword && (
              <div className="mt-2">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-gray-600">Fortaleza:</span>
                  <span className="text-xs font-medium text-gray-900">
                    {passwordStrength.label}
                  </span>
                </div>
                <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all ${passwordStrength.color}`}
                    style={{ width: `${(passwordStrength.level / 5) * 100}%` }}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Confirm Password */}
          <Input
            label="Confirmar nueva contraseña"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            error={errors.confirmPassword}
            placeholder="Repite la nueva contraseña"
            icon={Lock}
            required
          />

          {/* Success Message */}
          {newPassword && confirmPassword && newPassword === confirmPassword && !errors.confirmPassword && (
            <div className="p-3 bg-green-50 border border-green-200 rounded-lg flex items-start gap-2">
              <CheckCircle className="h-5 w-5 text-green-600 shrink-0 mt-0.5" />
              <p className="text-sm text-green-800">Las contraseñas coinciden</p>
            </div>
          )}

          {/* Security Tips */}
          <div className="p-3 bg-status-info-light border border-status-info-border rounded-lg">
            <div className="flex items-start gap-2">
              <AlertCircle className="h-4 w-4 text-status-info-text shrink-0 mt-0.5" />
              <div className="text-xs text-status-info-text">
                <p className="font-medium mb-1">Recomendaciones de seguridad:</p>
                <ul className="list-disc list-inside space-y-0.5">
                  <li>Usa al menos 8 caracteres</li>
                  <li>Combina mayúsculas y minúsculas</li>
                  <li>Incluye números y símbolos</li>
                  <li>Evita palabras comunes o información personal</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </DialogContent>

      <DialogFooter>
        <Button onClick={handleClose} variant="outline" disabled={isLoading}>
          Cancelar
        </Button>
        <Button
          onClick={handleSubmit}
          disabled={isLoading}
          className="bg-gradient-to-r from-primary-600 to-cyan-600"
        >
          {isLoading ? 'Cambiando...' : 'Cambiar Contraseña'}
        </Button>
      </DialogFooter>
    </Dialog>
  )
}

export default ChangePasswordModal
