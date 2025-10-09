import { useMutation, useQueryClient } from '@tanstack/react-query'
import { userService } from '@/services/userService'
import { userKeys, queryKeyUtils } from '@/lib/queryKeys'
import { useAppStore } from '@/store/app'
import { useAuthenticatedMutationDefaults, createMutationOptions } from '@/hooks/useGlobalMutationDefaults'
import type { 
  CreateUserData, 
  UpdateUserData, 
  UserResponse,
  UsersListResponse
} from '@/services/userService'
import type { User, UserRole } from '@/types'

/**
 * Hook for creating a new user with optimistic updates and global error handling
 */
export const useCreateUser = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    ...useAuthenticatedMutationDefaults('crear usuario', {
      showSuccessNotification: true,
      successMessage: 'Usuario creado correctamente'
    }),
    mutationFn: userService.createUser,
    onMutate: async (newUserData: CreateUserData) => {
      // Cancel any outgoing refetches for user lists
      await queryClient.cancelQueries({ queryKey: userKeys.lists() })
      
      // Snapshot the previous user list
      const previousUsers = queryClient.getQueryData(userKeys.list())
      
      // Create optimistic user object
      const optimisticUser: User = {
        id: `temp-${Date.now()}`, // Temporary ID
        email: newUserData.email,
        display_name: newUserData.display_name || newUserData.full_name || '',
        full_name: newUserData.full_name || newUserData.display_name || '',
        organization: newUserData.organization || '',
        role: newUserData.role,
        is_active: newUserData.is_active ?? true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        last_login: null,
        email_verified: false,
        profile_image: null,
      }
      
      // Optimistically update the user list cache
      if (previousUsers && typeof previousUsers === 'object' && 'users' in previousUsers) {
        const usersList = previousUsers as UsersListResponse
        const updatedUsers: UsersListResponse = {
          ...usersList,
          users: [optimisticUser, ...usersList.users],
          total: usersList.total + 1,
        }
        queryClient.setQueryData(userKeys.list(), updatedUsers)
      }
      
      return { previousUsers, optimisticUser }
    },
    onError: (error: any, newUserData, context) => {
      // Rollback optimistic update
      if (context?.previousUsers) {
        queryClient.setQueryData(userKeys.list(), context.previousUsers)
      }
      // Global error handling will show the notification
    },
    onSuccess: (response: UserResponse, newUserData) => {
      // Global success handler will show the notification
      // Custom success logic can go here if needed
    },
    onSettled: () => {
      // Always refetch user lists and stats to ensure consistency
      queryClient.invalidateQueries({ queryKey: userKeys.lists() })
      queryClient.invalidateQueries({ queryKey: userKeys.stats() })
    },
  })
}

/**
 * Hook for updating a user with optimistic updates
 */
export const useUpdateUser = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateUserData }) => 
      userService.updateUser(id, data),
    onMutate: async ({ id, data }) => {
      // Cancel any outgoing refetches for this user
      await queryClient.cancelQueries({ queryKey: userKeys.detail(id) })
      await queryClient.cancelQueries({ queryKey: userKeys.lists() })
      
      // Snapshot the previous user data
      const previousUser = queryClient.getQueryData<User>(userKeys.detail(id))
      const previousUserList = queryClient.getQueryData(userKeys.list())
      
      // Optimistically update the user detail cache
      if (previousUser) {
        const optimisticUser = { ...previousUser, ...data, updated_at: new Date().toISOString() }
        queryClient.setQueryData(userKeys.detail(id), optimisticUser)
        
        // Also update the user in the list cache if it exists
        if (previousUserList && typeof previousUserList === 'object' && 'users' in previousUserList) {
          const usersList = previousUserList as UsersListResponse
          const updatedUsers: UsersListResponse = {
            ...usersList,
            users: usersList.users.map((user: User) =>
              user.id === id ? optimisticUser : user
            ),
          }
          queryClient.setQueryData(userKeys.list(), updatedUsers)
        }
      }
      
      return { previousUser, previousUserList }
    },
    onError: (error: any, { id }, context) => {
      // Rollback optimistic updates
      if (context?.previousUser) {
        queryClient.setQueryData(userKeys.detail(id), context.previousUser)
      }
      if (context?.previousUserList) {
        queryClient.setQueryData(userKeys.list(), context.previousUserList)
      }
      
      // Show error notification
      useAppStore.getState().addNotification({
        type: 'error',
        title: 'Error al actualizar usuario',
        message: error?.message || 'No se pudo actualizar el usuario',
        duration: 5000,
      })
    },
    onSuccess: (response: UserResponse, { id }) => {
      // Update caches with server response
      queryClient.setQueryData(userKeys.detail(id), response.user)
      
      // Show success notification
      useAppStore.getState().addNotification({
        type: 'success',
        title: 'Usuario actualizado',
        message: `Usuario ${response.user.display_name || response.user.email} actualizado correctamente`,
        duration: 3000,
      })
    },
    onSettled: (data, error, { id }) => {
      // Always refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: userKeys.detail(id) })
      queryClient.invalidateQueries({ queryKey: userKeys.lists() })
      queryClient.invalidateQueries({ queryKey: userKeys.stats() })
    },
  })
}

/**
 * Hook for deleting a user with optimistic updates
 */
export const useDeleteUser = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: userService.deleteUser,
    onMutate: async (userId: string) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: userKeys.detail(userId) })
      await queryClient.cancelQueries({ queryKey: userKeys.lists() })
      
      // Snapshot the previous data
      const previousUser = queryClient.getQueryData<User>(userKeys.detail(userId))
      const previousUserList = queryClient.getQueryData(userKeys.list())
      
      // Optimistically remove user from list cache
      if (previousUserList && typeof previousUserList === 'object' && 'users' in previousUserList) {
        const usersList = previousUserList as UsersListResponse
        const updatedUsers: UsersListResponse = {
          ...usersList,
          users: usersList.users.filter((user: User) => user.id !== userId),
          total: Math.max(0, usersList.total - 1),
        }
        queryClient.setQueryData(userKeys.list(), updatedUsers)
      }
      
      // Remove user detail from cache
      queryClient.removeQueries({ queryKey: userKeys.detail(userId) })
      
      return { previousUser, previousUserList }
    },
    onError: (error: any, userId, context) => {
      // Rollback optimistic updates
      if (context?.previousUser) {
        queryClient.setQueryData(userKeys.detail(userId), context.previousUser)
      }
      if (context?.previousUserList) {
        queryClient.setQueryData(userKeys.list(), context.previousUserList)
      }
      
      // Show error notification
      useAppStore.getState().addNotification({
        type: 'error',
        title: 'Error al eliminar usuario',
        message: error?.message || 'No se pudo eliminar el usuario',
        duration: 5000,
      })
    },
    onSuccess: (data, userId, context) => {
      const userName = context?.previousUser?.display_name || context?.previousUser?.email || 'Usuario'
      
      // Show success notification
      useAppStore.getState().addNotification({
        type: 'success',
        title: 'Usuario eliminado',
        message: `${userName} ha sido eliminado correctamente`,
        duration: 3000,
      })
    },
    onSettled: () => {
      // Always refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: userKeys.lists() })
      queryClient.invalidateQueries({ queryKey: userKeys.stats() })
    },
  })
}

/**
 * Hook for updating user role with optimistic updates
 */
export const useUpdateUserRole = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, role }: { id: string; role: UserRole }) => 
      userService.updateUserRole(id, role),
    onMutate: async ({ id, role }) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: userKeys.detail(id) })
      await queryClient.cancelQueries({ queryKey: userKeys.lists() })
      
      // Snapshot the previous data
      const previousUser = queryClient.getQueryData<User>(userKeys.detail(id))
      const previousUserList = queryClient.getQueryData(userKeys.list())
      
      // Optimistically update the user role
      if (previousUser) {
        const optimisticUser = { ...previousUser, role, updated_at: new Date().toISOString() }
        queryClient.setQueryData(userKeys.detail(id), optimisticUser)
        
        // Also update in list cache
        if (previousUserList && typeof previousUserList === 'object' && 'users' in previousUserList) {
          const usersList = previousUserList as UsersListResponse
          const updatedUsers: UsersListResponse = {
            ...usersList,
            users: usersList.users.map((user: User) =>
              user.id === id ? optimisticUser : user
            ),
          }
          queryClient.setQueryData(userKeys.list(), updatedUsers)
        }
      }
      
      return { previousUser, previousUserList }
    },
    onError: (error: any, { id }, context) => {
      // Rollback optimistic updates
      if (context?.previousUser) {
        queryClient.setQueryData(userKeys.detail(id), context.previousUser)
      }
      if (context?.previousUserList) {
        queryClient.setQueryData(userKeys.list(), context.previousUserList)
      }
      
      // Show error notification
      useAppStore.getState().addNotification({
        type: 'error',
        title: 'Error al actualizar rol',
        message: error?.message || 'No se pudo actualizar el rol del usuario',
        duration: 5000,
      })
    },
    onSuccess: (response: UserResponse, { role }) => {
      const roleName = role === 'ADMIN' ? 'Administrador' : role === 'EXPERT' ? 'Experto' : 'Usuario'
      
      // Show success notification
      useAppStore.getState().addNotification({
        type: 'success',
        title: 'Rol actualizado',
        message: `El rol ha sido cambiado a ${roleName}`,
        duration: 3000,
      })
    },
    onSettled: (data, error, { id }) => {
      // Always refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: userKeys.detail(id) })
      queryClient.invalidateQueries({ queryKey: userKeys.lists() })
      queryClient.invalidateQueries({ queryKey: userKeys.stats() })
    },
  })
}

/**
 * Hook for activating/deactivating a user
 */
export const useToggleUserStatus = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, activate }: { id: string; activate: boolean }) => 
      activate ? userService.activateUser(id) : userService.deactivateUser(id),
    onMutate: async ({ id, activate }) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: userKeys.detail(id) })
      await queryClient.cancelQueries({ queryKey: userKeys.lists() })
      
      // Snapshot the previous data
      const previousUser = queryClient.getQueryData<User>(userKeys.detail(id))
      const previousUserList = queryClient.getQueryData(userKeys.list())
      
      // Optimistically update the user status
      if (previousUser) {
        const optimisticUser = { 
          ...previousUser, 
          is_active: activate, 
          updated_at: new Date().toISOString() 
        }
        queryClient.setQueryData(userKeys.detail(id), optimisticUser)
        
        // Also update in list cache
        if (previousUserList && typeof previousUserList === 'object' && 'users' in previousUserList) {
          const usersList = previousUserList as UsersListResponse
          const updatedUsers: UsersListResponse = {
            ...usersList,
            users: usersList.users.map((user: User) =>
              user.id === id ? optimisticUser : user
            ),
          }
          queryClient.setQueryData(userKeys.list(), updatedUsers)
        }
      }
      
      return { previousUser, previousUserList, activate }
    },
    onError: (error: any, { id }, context) => {
      // Rollback optimistic updates
      if (context?.previousUser) {
        queryClient.setQueryData(userKeys.detail(id), context.previousUser)
      }
      if (context?.previousUserList) {
        queryClient.setQueryData(userKeys.list(), context.previousUserList)
      }
      
      const action = context?.activate ? 'activar' : 'desactivar'
      
      // Show error notification
      useAppStore.getState().addNotification({
        type: 'error',
        title: `Error al ${action} usuario`,
        message: error?.message || `No se pudo ${action} el usuario`,
        duration: 5000,
      })
    },
    onSuccess: (response: UserResponse, { activate }) => {
      const action = activate ? 'activado' : 'desactivado'
      
      // Show success notification
      useAppStore.getState().addNotification({
        type: 'success',
        title: 'Estado actualizado',
        message: `El usuario ha sido ${action} correctamente`,
        duration: 3000,
      })
    },
    onSettled: (data, error, { id }) => {
      // Always refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: userKeys.detail(id) })
      queryClient.invalidateQueries({ queryKey: userKeys.lists() })
      queryClient.invalidateQueries({ queryKey: userKeys.stats() })
    },
  })
}

/**
 * Hook for resetting user password (admin operation)
 */
export const useResetUserPassword = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, newPassword }: { id: string; newPassword: string }) => 
      userService.resetUserPassword(id, newPassword),
    onSuccess: (data, { id }) => {
      // Get user data for notification
      const user = queryClient.getQueryData<User>(userKeys.detail(id))
      const userName = user?.display_name || user?.email || 'Usuario'
      
      // Show success notification
      useAppStore.getState().addNotification({
        type: 'success',
        title: 'Contraseña restablecida',
        message: `La contraseña de ${userName} ha sido restablecida`,
        duration: 3000,
      })
    },
    onError: (error: any) => {
      // Show error notification
      useAppStore.getState().addNotification({
        type: 'error',
        title: 'Error al restablecer contraseña',
        message: error?.message || 'No se pudo restablecer la contraseña',
        duration: 5000,
      })
    },
  })
}

/**
 * Hook for bulk user operations
 */
export const useBulkUpdateUsers = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ userIds, data }: { userIds: string[]; data: Partial<UpdateUserData> }) => 
      userService.bulkUpdateUsers(userIds, data),
    onSuccess: (data, { userIds }) => {
      // Show success notification
      useAppStore.getState().addNotification({
        type: 'success',
        title: 'Usuarios actualizados',
        message: `${userIds.length} usuarios han sido actualizados correctamente`,
        duration: 3000,
      })
      
      // Invalidate all user-related queries
      queryClient.invalidateQueries({ queryKey: userKeys.all })
    },
    onError: (error: any) => {
      // Show error notification
      useAppStore.getState().addNotification({
        type: 'error',
        title: 'Error en actualización masiva',
        message: error?.message || 'No se pudieron actualizar los usuarios',
        duration: 5000,
      })
    },
  })
}

/**
 * Hook for bulk user deletion
 */
export const useBulkDeleteUsers = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: userService.bulkDeleteUsers,
    onSuccess: (data, userIds) => {
      // Show success notification
      useAppStore.getState().addNotification({
        type: 'success',
        title: 'Usuarios eliminados',
        message: `${userIds.length} usuarios han sido eliminados correctamente`,
        duration: 3000,
      })
      
      // Invalidate all user-related queries
      queryClient.invalidateQueries({ queryKey: userKeys.all })
    },
    onError: (error: any) => {
      // Show error notification
      useAppStore.getState().addNotification({
        type: 'error',
        title: 'Error en eliminación masiva',
        message: error?.message || 'No se pudieron eliminar los usuarios',
        duration: 5000,
      })
    },
  })
}