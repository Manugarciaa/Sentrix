import React, { useState, useEffect } from 'react'
import { User as UserIcon, Mail, Shield, Calendar, Activity, Key, Edit2, Save, X } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Avatar } from '@/components/ui/Avatar'
import { RoleBadge } from '@/components/domain/RoleBadge'
import { Badge } from '@/components/ui/Badge'
import { ChangePasswordModal } from '@/components/domain/ChangePasswordModal'
import { ActivityTimeline, TimelineActivity } from '@/components/domain/ActivityTimeline'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { config } from '@/lib/config'
import { useAuth } from '@/hooks/useAuth'
import { useUpdateProfile, useChangePassword } from '@/hooks/useAuthMutations'

interface UserStats {
  total_analyses: number
  total_detections: number
  validated_detections: number
  created_reports: number
}

const ProfilePage: React.FC = () => {
  // React Query hooks
  const { user, isLoading: isUserLoading } = useAuth()
  const updateProfile = useUpdateProfile()
  const changePassword = useChangePassword()

  // Local state for editing
  const [isEditingName, setIsEditingName] = useState(false)
  const [editedName, setEditedName] = useState('')
  const [isEditingOrg, setIsEditingOrg] = useState(false)
  const [editedOrg, setEditedOrg] = useState('')

  // Stats and activities state (will be migrated to React Query in future tasks)
  const [stats, setStats] = useState<UserStats | null>(null)
  const [activities, setActivities] = useState<TimelineActivity[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const [passwordModalOpen, setPasswordModalOpen] = useState(false)

  // Update local state when user data changes
  useEffect(() => {
    if (user) {
      setEditedName(user.display_name || user.full_name || user.name || '')
      setEditedOrg(user.organization || '')
    }
  }, [user])

  useEffect(() => {
    fetchUserData()
  }, [])

  const fetchUserData = async () => {
    try {
      setIsLoading(true)

      // Fetch user stats and activities in parallel
      const [statsResponse, activitiesResponse] = await Promise.all([
        fetch(`${config.api.baseUrl}/api/users/me/stats`),
        fetch(`${config.api.baseUrl}/api/users/me/activities`),
      ])

      if (statsResponse.ok) {
        const statsData = await statsResponse.json()
        setStats(statsData)
      }

      if (activitiesResponse.ok) {
        const activitiesData = await activitiesResponse.json()
        setActivities(activitiesData.activities || [])
      }
    } catch (error) {
      console.error('Error fetching user data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSaveName = async () => {
    if (!editedName?.trim()) {
      return
    }

    try {
      await updateProfile.mutateAsync({ display_name: editedName.trim() })
      setIsEditingName(false)
    } catch (error) {
      // Error handling is done in the mutation hook
      console.error('Error updating name:', error)
    }
  }

  const handleSaveOrganization = async () => {
    try {
      await updateProfile.mutateAsync({ organization: editedOrg?.trim() || null })
      setIsEditingOrg(false)
    } catch (error) {
      // Error handling is done in the mutation hook
      console.error('Error updating organization:', error)
    }
  }

  const handleChangePassword = async (currentPassword: string, newPassword: string) => {
    await changePassword.mutateAsync({
      current_password: currentPassword,
      new_password: newPassword,
    })
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
    })
  }

  if (isUserLoading || !user) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-gray-900">Mi Perfil</h1>
        <p className="text-base text-gray-700 mt-2">
          Gestiona tu información personal y configuración de cuenta
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Profile Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Profile Card */}
          <Card className="p-6">
            <div className="flex items-start gap-6">
              {/* Avatar */}
              <div className="shrink-0">
                <Avatar name={user.display_name || user.full_name || user.name || user.email} src={user.avatar} size="xl" />
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full mt-3 text-xs"
                  disabled
                >
                  Cambiar foto
                </Button>
              </div>

              {/* Info */}
              <div className="flex-1 space-y-4">
                {/* Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nombre completo
                  </label>
                  {isEditingName ? (
                    <div className="flex items-center gap-2">
                      <Input
                        value={editedName}
                        onChange={(e) => setEditedName(e.target.value)}
                        placeholder="Tu nombre"
                        className="flex-1"
                        disabled={updateProfile.isPending}
                      />
                      <Button
                        onClick={handleSaveName}
                        size="sm"
                        disabled={updateProfile.isPending || !editedName?.trim()}
                        className="bg-green-600 hover:bg-green-700"
                      >
                        {updateProfile.isPending ? (
                          <LoadingSpinner size="sm" />
                        ) : (
                          <Save className="h-4 w-4" />
                        )}
                      </Button>
                      <Button
                        onClick={() => {
                          setEditedName(user.display_name || user.full_name || user.name || '')
                          setIsEditingName(false)
                        }}
                        size="sm"
                        variant="outline"
                        disabled={updateProfile.isPending}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <p className="text-base font-medium text-gray-900">{user.display_name || user.full_name || user.name}</p>
                      <Button
                        onClick={() => {
                          setEditedName(user.display_name || user.full_name || user.name || '')
                          setIsEditingName(true)
                        }}
                        size="sm"
                        variant="ghost"
                        className="text-primary-600"
                      >
                        <Edit2 className="h-4 w-4" />
                      </Button>
                    </div>
                  )}
                </div>

                {/* Email */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                  </label>
                  <div className="flex items-center gap-2">
                    <Mail className="h-4 w-4 text-gray-400" />
                    <p className="text-sm text-gray-900">{user.email}</p>
                    <Badge variant="success" className="text-xs">Verificado</Badge>
                  </div>
                </div>

                {/* Role */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Rol
                  </label>
                  <div className="flex items-center gap-2">
                    <Shield className="h-4 w-4 text-gray-400" />
                    <RoleBadge role={user.role} />
                  </div>
                </div>

                {/* Organization */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Organización
                  </label>
                  {isEditingOrg ? (
                    <div className="flex items-center gap-2">
                      <Input
                        value={editedOrg}
                        onChange={(e) => setEditedOrg(e.target.value)}
                        placeholder="Tu organización"
                        className="flex-1"
                        disabled={updateProfile.isPending}
                      />
                      <Button
                        onClick={handleSaveOrganization}
                        size="sm"
                        disabled={updateProfile.isPending}
                        className="bg-green-600 hover:bg-green-700"
                      >
                        {updateProfile.isPending ? (
                          <LoadingSpinner size="sm" />
                        ) : (
                          <Save className="h-4 w-4" />
                        )}
                      </Button>
                      <Button
                        onClick={() => {
                          setEditedOrg(user.organization || '')
                          setIsEditingOrg(false)
                        }}
                        size="sm"
                        variant="outline"
                        disabled={updateProfile.isPending}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <p className="text-sm text-gray-900">
                        {user.organization || 'No especificada'}
                      </p>
                      <Button
                        onClick={() => {
                          setEditedOrg(user.organization || '')
                          setIsEditingOrg(true)
                        }}
                        size="sm"
                        variant="ghost"
                        className="text-primary-600"
                        disabled={updateProfile.isPending}
                      >
                        <Edit2 className="h-4 w-4" />
                      </Button>
                    </div>
                  )}
                </div>

                {/* Registration Date */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Fecha de registro
                  </label>
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-gray-400" />
                    <p className="text-sm text-gray-900">{formatDate(user.created_at)}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Change Password Button */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <Button
                onClick={() => setPasswordModalOpen(true)}
                variant="outline"
                className="gap-2"
              >
                <Key className="h-4 w-4" />
                Cambiar Contraseña
              </Button>
            </div>
          </Card>

          {/* Activity Timeline */}
          <Card className="p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Actividad Reciente
            </h2>

            {isLoading ? (
              <div className="flex justify-center py-8">
                <LoadingSpinner />
              </div>
            ) : (
              <ActivityTimeline activities={activities} />
            )}
          </Card>
        </div>

        {/* Right Column - Stats */}
        <div className="space-y-6">
          {/* Stats Card */}
          <Card className="p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Estadísticas</h2>

            {isLoading ? (
              <div className="flex justify-center py-8">
                <LoadingSpinner />
              </div>
            ) : stats ? (
              <div className="space-y-4">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-700 mb-1">Análisis Totales</p>
                  <p className="text-3xl font-bold text-blue-900">{stats.total_analyses}</p>
                </div>

                <div className="p-4 bg-red-50 rounded-lg">
                  <p className="text-sm text-red-700 mb-1">Detecciones</p>
                  <p className="text-3xl font-bold text-red-900">{stats.total_detections}</p>
                </div>

                {(user.role === 'ADMIN' || user.role === 'EXPERT') && (
                  <div className="p-4 bg-purple-50 rounded-lg">
                    <p className="text-sm text-purple-700 mb-1">Validaciones</p>
                    <p className="text-3xl font-bold text-purple-900">
                      {stats.validated_detections}
                    </p>
                  </div>
                )}

                <div className="p-4 bg-green-50 rounded-lg">
                  <p className="text-sm text-green-700 mb-1">Reportes Generados</p>
                  <p className="text-3xl font-bold text-green-900">{stats.created_reports}</p>
                </div>
              </div>
            ) : null}
          </Card>

          {/* Account Status */}
          <Card className="p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Estado de Cuenta</h2>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">Estado</span>
                <Badge variant={user.is_active ? 'success' : 'default'}>
                  {user.is_active ? 'Activa' : 'Inactiva'}
                </Badge>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">Último acceso</span>
                <span className="text-sm font-medium text-gray-900">
                  {formatDate(user.last_login)}
                </span>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Change Password Modal */}
      <ChangePasswordModal
        open={passwordModalOpen}
        onClose={() => setPasswordModalOpen(false)}
        onSubmit={handleChangePassword}
      />
    </div>
  )
}

export default ProfilePage
