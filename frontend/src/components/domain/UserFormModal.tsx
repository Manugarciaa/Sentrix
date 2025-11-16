import React, { useState, useEffect } from 'react'
import { User as UserIcon, Mail, Shield, AlertCircle } from 'lucide-react'
import { Dialog, DialogHeader, DialogContent, DialogFooter } from '@/components/ui/Dialog'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Checkbox } from '@/components/ui/Checkbox'
import { useCreateUser, useUpdateUser } from '@/hooks/useUserMutations'
import type { User, UserRole } from '@/types'
import type { CreateUserData, UpdateUserData } from '@/services/userService'

export interface UserFormData {
  display_name: string
  email: string
  role: UserRole
  is_active: boolean
  password?: string
}

export interface UserFormModalProps {
  open: boolean
  onClose: () => void
  onSuccess?: () => void
  user?: User | null
  mode: 'create' | 'edit'
}

export const UserFormModal: React.FC<UserFormModalProps> = ({
  open,
  onClose,
  onSuccess,
  user,
  mode,
}) => {
  // React Query mutations
  const createUserMutation = useCreateUser()
  const updateUserMutation = useUpdateUser()

  const [formData, setFormData] = useState<UserFormData>({
    display_name: '',
    email: '',
    role: 'USER' as UserRole,
    is_active: true,
    password: '',
  })

  const [errors, setErrors] = useState<Partial<Record<keyof UserFormData, string>>>({})

  // Determine loading state from mutations
  const isLoading = createUserMutation.isPending || updateUserMutation.isPending

  useEffect(() => {
    if (user && mode === 'edit') {
      setFormData({
        display_name: user.display_name || user.full_name || user.name || '',
        email: user.email,
        role: user.role,
        is_active: user.is_active,
      })
    } else if (mode === 'create') {
      setFormData({
        display_name: '',
        email: '',
        role: 'USER' as UserRole,
        is_active: true,
        password: '',
      })
    }
    setErrors({})
  }, [user, mode, open])

  const validateForm = (): boolean => {
    const newErrors: Partial<Record<keyof UserFormData, string>> = {}

    if (!formData.display_name?.trim()) {
      newErrors.display_name = 'El nombre es requerido'
    }

    if (!formData.email?.trim()) {
      newErrors.email = 'El email es requerido'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Email inválido'
    }

    if (mode === 'create' && !formData.password) {
      newErrors.password = 'La contraseña es requerida'
    }

    if (mode === 'create' && formData.password && formData.password.length < 6) {
      newErrors.password = 'La contraseña debe tener al menos 6 caracteres'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async () => {
    if (!validateForm()) return

    try {
      if (mode === 'create') {
        // Prepare create user data
        const createData: CreateUserData = {
          email: formData.email,
          password: formData.password!,
          display_name: formData.display_name,
          role: formData.role,
          is_active: formData.is_active,
        }
        
        await createUserMutation.mutateAsync(createData)
      } else if (user) {
        // Prepare update user data
        const updateData: UpdateUserData = {
          display_name: formData.display_name,
          role: formData.role,
          is_active: formData.is_active,
        }
        
        await updateUserMutation.mutateAsync({ id: user.id, data: updateData })
      }
      
      // Call success callback and close modal
      onSuccess?.()
      handleClose()
    } catch (error) {
      // Error handling is done by the mutation hooks
      console.error('Error submitting form:', error)
    }
  }

  const handleClose = () => {
    // Reset form data
    setFormData({
      display_name: '',
      email: '',
      role: 'USER' as UserRole,
      is_active: true,
      password: '',
    })
    setErrors({})
    
    // Reset mutation states
    createUserMutation.reset()
    updateUserMutation.reset()
    
    onClose()
  }

  return (
    <Dialog open={open} onClose={handleClose} size="md">
      <DialogHeader>
        <h3 className="text-xl font-bold text-gray-900">
          {mode === 'create' ? 'Crear Usuario' : 'Editar Usuario'}
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          {mode === 'create'
            ? 'Completa los datos del nuevo usuario'
            : 'Actualiza la información del usuario'}
        </p>
      </DialogHeader>

      <DialogContent>
        <div className="space-y-4">
          {/* Name */}
          <Input
            label="Nombre completo"
            value={formData.display_name}
            onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
            error={errors.display_name}
            placeholder="Ej: Juan Pérez"
            icon={UserIcon}
            required
          />

          {/* Email */}
          <Input
            label="Email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            error={errors.email}
            placeholder="usuario@ejemplo.com"
            icon={Mail}
            required
            disabled={mode === 'edit'}
          />

          {/* Password (only for create) */}
          {mode === 'create' && (
            <Input
              label="Contraseña"
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              error={errors.password}
              placeholder="Mínimo 6 caracteres"
              required
            />
          )}

          {/* Role */}
          <div>
            <Select
              label="Rol"
              options={[
                { value: 'USER', label: 'Usuario (solo lectura y creación)' },
                { value: 'EXPERT', label: 'Experto (validar detecciones)' },
                { value: 'ADMIN', label: 'Administrador (acceso completo)' },
              ]}
              value={formData.role}
              onChange={(value) => setFormData({ ...formData, role: value as UserRole })}
              required
            />
            <div className="mt-2 p-3 bg-status-info-light border border-status-info-border rounded-lg">
              <div className="flex items-start gap-2">
                <Shield className="h-4 w-4 text-status-info-text shrink-0 mt-0.5" />
                <p className="text-xs text-status-info-text">
                  {formData.role === 'ADMIN' && 'Puede gestionar usuarios, validar detecciones y acceder a todas las funciones'}
                  {formData.role === 'EXPERT' && 'Puede validar detecciones y generar reportes avanzados'}
                  {formData.role === 'USER' && 'Puede crear análisis y visualizar sus propios resultados'}
                </p>
              </div>
            </div>
          </div>

          {/* Active Status */}
          <div className="pt-2">
            <Checkbox
              label="Usuario activo"
              description="Los usuarios inactivos no pueden iniciar sesión"
              checked={formData.is_active}
              onChange={(checked) => setFormData({ ...formData, is_active: checked })}
            />
          </div>

          {/* Warning for editing */}
          {mode === 'edit' && !formData.is_active && (
            <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
              <div className="flex items-start gap-2">
                <AlertCircle className="h-4 w-4 text-amber-600 shrink-0 mt-0.5" />
                <p className="text-xs text-amber-900">
                  Al desactivar este usuario, no podrá iniciar sesión hasta que lo reactives.
                </p>
              </div>
            </div>
          )}

          {/* Mutation Error Display */}
          {(createUserMutation.error || updateUserMutation.error) && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-start gap-2">
                <AlertCircle className="h-4 w-4 text-red-600 shrink-0 mt-0.5" />
                <p className="text-xs text-red-900">
                  {createUserMutation.error?.message || updateUserMutation.error?.message || 'Ha ocurrido un error'}
                </p>
              </div>
            </div>
          )}
        </div>
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
          disabled={isLoading}
          className="bg-gradient-to-r from-primary-600 to-cyan-600"
        >
          {isLoading ? 'Guardando...' : mode === 'create' ? 'Crear Usuario' : 'Guardar Cambios'}
        </Button>
      </DialogFooter>
    </Dialog>
  )
}

export default UserFormModal
