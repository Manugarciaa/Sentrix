import React, { useState, useEffect } from 'react'
import { Users as UsersIcon, Plus, Search, Trash2, Edit, MoreVertical } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Table, TableColumn } from '@/components/ui/Table'
import { Avatar } from '@/components/ui/Avatar'
import { RoleBadge } from '@/components/domain/RoleBadge'
import { Badge } from '@/components/ui/Badge'
import { UserFormModal } from '@/components/domain/UserFormModal'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { EmptyState } from '@/components/domain/EmptyState'
import { config } from '@/lib/config'
import { useAuthStore } from '@/store/auth'
import type { User, UserRole } from '@/types'

const UsersPage: React.FC = () => {
  const { user: currentUser } = useAuthStore()

  const [users, setUsers] = useState<User[]>([])
  const [filteredUsers, setFilteredUsers] = useState<User[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // Filters
  const [searchQuery, setSearchQuery] = useState('')
  const [roleFilter, setRoleFilter] = useState<string>('')
  const [statusFilter, setStatusFilter] = useState<string>('')

  // Modal state
  const [modalOpen, setModalOpen] = useState(false)
  const [modalMode, setModalMode] = useState<'create' | 'edit'>('create')
  const [selectedUser, setSelectedUser] = useState<User | null>(null)

  useEffect(() => {
    fetchUsers()
  }, [])

  useEffect(() => {
    filterUsers()
  }, [users, searchQuery, roleFilter, statusFilter])

  const fetchUsers = async () => {
    try {
      setIsLoading(true)

      const token = localStorage.getItem('token')
      const response = await fetch(`${config.api.baseUrl}/api/v1/users`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setUsers(data.users || [])
      }
    } catch (error) {
      console.error('Error fetching users:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const filterUsers = () => {
    let filtered = [...users]

    // Search by name or email
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(
        (user) =>
          user.name.toLowerCase().includes(query) ||
          user.email.toLowerCase().includes(query)
      )
    }

    // Filter by role
    if (roleFilter) {
      filtered = filtered.filter((user) => user.role === roleFilter)
    }

    // Filter by status
    if (statusFilter === 'active') {
      filtered = filtered.filter((user) => user.is_active)
    } else if (statusFilter === 'inactive') {
      filtered = filtered.filter((user) => !user.is_active)
    }

    setFilteredUsers(filtered)
  }

  const handleModalSuccess = () => {
    // Refresh users list after successful create/update
    fetchUsers()
    setModalOpen(false)
    setSelectedUser(null)
  }

  const handleDeleteUser = async (user: User) => {
    if (user.id === currentUser?.id) {
      alert('No puedes eliminar tu propio usuario')
      return
    }

    const displayName = user.display_name || user.full_name || user.name || user.email
    if (!confirm(`¿Estás seguro de eliminar al usuario "${displayName}"?`)) {
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${config.api.baseUrl}/api/v1/users/${user.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        setUsers(users.filter((u) => u.id !== user.id))
      } else {
        throw new Error('Error al eliminar usuario')
      }
    } catch (error) {
      console.error('Error deleting user:', error)
      alert('Error al eliminar el usuario. Por favor intenta nuevamente.')
    }
  }

  const handleOpenCreateModal = () => {
    setModalMode('create')
    setSelectedUser(null)
    setModalOpen(true)
  }

  const handleOpenEditModal = (user: User) => {
    setModalMode('edit')
    setSelectedUser(user)
    setModalOpen(true)
  }

  const handleResetFilters = () => {
    setSearchQuery('')
    setRoleFilter('')
    setStatusFilter('')
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Nunca'
    return new Date(dateString).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    })
  }

  const columns: TableColumn<User>[] = [
    {
      key: 'user',
      label: 'Usuario',
      render: (user) => (
        <div className="flex items-center gap-3">
          <Avatar name={user.name} src={user.avatar} />
          <div>
            <p className="font-medium text-foreground">{user.name}</p>
            <p className="text-xs text-muted-foreground">{user.email}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'role',
      label: 'Rol',
      align: 'center',
      render: (user) => <RoleBadge role={user.role} />,
    },
    {
      key: 'status',
      label: 'Estado',
      align: 'center',
      render: (user) =>
        user.is_active ? (
          <Badge variant="success">Activo</Badge>
        ) : (
          <Badge variant="default">Inactivo</Badge>
        ),
    },
    {
      key: 'last_login',
      label: 'Último acceso',
      render: (user) => (
        <span className="text-sm text-muted-foreground">{formatDate(user.last_login)}</span>
      ),
    },
    {
      key: 'created_at',
      label: 'Fecha de registro',
      render: (user) => (
        <span className="text-sm text-muted-foreground">{formatDate(user.created_at)}</span>
      ),
    },
    {
      key: 'actions',
      label: 'Acciones',
      align: 'right',
      render: (user) => (
        <div className="flex items-center justify-end gap-2">
          <Button
            onClick={() => handleOpenEditModal(user)}
            variant="ghost"
            size="sm"
            className="text-primary-600 hover:text-primary-700 hover:bg-primary-50 dark:bg-primary-950/30"
          >
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            onClick={() => handleDeleteUser(user)}
            variant="ghost"
            size="sm"
            className="text-red-600 hover:text-red-700 hover:bg-red-50"
            disabled={user.id === currentUser?.id}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      ),
    },
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-sm text-muted-foreground">Cargando usuarios...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold text-foreground">Usuarios</h1>
          <p className="text-base text-muted-foreground mt-2">
            Gestiona los usuarios del sistema ({users.length} total)
          </p>
        </div>

        <Button
          onClick={handleOpenCreateModal}
          className="gap-2"
        >
          <Plus className="h-4 w-4" />
          Nuevo Usuario
        </Button>
      </div>

      {/* Filters */}
      <div className="bg-card rounded-xl border border-border p-4 shadow-sm">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="md:col-span-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                type="search"
                placeholder="Buscar por nombre o email..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          {/* Role Filter */}
          <Select
            options={[
              { value: '', label: 'Todos los roles' },
              { value: 'ADMIN', label: 'Administrador' },
              { value: 'EXPERT', label: 'Experto' },
              { value: 'USER', label: 'Usuario' },
            ]}
            value={roleFilter}
            onChange={setRoleFilter}
          />

          {/* Status Filter */}
          <Select
            options={[
              { value: '', label: 'Todos los estados' },
              { value: 'active', label: 'Activos' },
              { value: 'inactive', label: 'Inactivos' },
            ]}
            value={statusFilter}
            onChange={setStatusFilter}
          />
        </div>

        {/* Active Filters */}
        {(searchQuery || roleFilter || statusFilter) && (
          <div className="mt-3 flex items-center gap-2">
            <span className="text-xs text-muted-foreground">Filtros activos:</span>
            {searchQuery && (
              <Badge variant="default" className="text-xs">
                Búsqueda: {searchQuery}
              </Badge>
            )}
            {roleFilter && (
              <Badge variant="default" className="text-xs">
                Rol: {roleFilter}
              </Badge>
            )}
            {statusFilter && (
              <Badge variant="default" className="text-xs">
                Estado: {statusFilter === 'active' ? 'Activo' : 'Inactivo'}
              </Badge>
            )}
            <Button
              onClick={handleResetFilters}
              variant="ghost"
              size="sm"
              className="text-xs"
            >
              Limpiar filtros
            </Button>
          </div>
        )}
      </div>

      {/* Users Table */}
      {filteredUsers.length === 0 ? (
        <EmptyState
          icon={UsersIcon}
          title="No se encontraron usuarios"
          description={
            searchQuery || roleFilter || statusFilter
              ? 'No hay usuarios que coincidan con los filtros. Intenta ajustar los criterios de búsqueda.'
              : 'Aún no hay usuarios registrados. Crea el primero para comenzar.'
          }
          action={
            <div className="flex gap-3">
              {(searchQuery || roleFilter || statusFilter) && (
                <Button onClick={handleResetFilters} variant="outline">
                  Limpiar Filtros
                </Button>
              )}
              <Button
                onClick={handleOpenCreateModal}
              >
                <Plus className="h-4 w-4 mr-2" />
                Crear Usuario
              </Button>
            </div>
          }
        />
      ) : (
        <Table
          columns={columns}
          data={filteredUsers}
          keyExtractor={(user) => user.id}
        />
      )}

      {/* User Form Modal */}
      <UserFormModal
        open={modalOpen}
        onClose={() => {
          setModalOpen(false)
          setSelectedUser(null)
        }}
        onSuccess={handleModalSuccess}
        user={selectedUser}
        mode={modalMode}
      />
    </div>
  )
}

export default UsersPage
