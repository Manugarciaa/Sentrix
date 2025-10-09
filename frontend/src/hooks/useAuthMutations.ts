import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { authService } from '@/services/authService'
import { authKeys, queryKeyUtils } from '@/lib/queryKeys'
import { useAuthStore } from '@/store/auth'
import { useAppStore } from '@/store/app'
import { config } from '@/lib/config'
import type { 
  LoginCredentials, 
  RegisterData, 
  ProfileUpdateData, 
  PasswordChangeData,
  LoginResponse,
  RegisterResponse,
  User
} from '@/services/authService'

/**
 * Hook for login mutation with proper error handling and token management
 */
export const useLogin = () => {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  
  return useMutation({
    mutationFn: authService.login,
    onMutate: () => {
      // Clear any existing auth errors
      useAuthStore.getState().clearError()
      // Set loading state
      useAuthStore.setState({ isLoading: true })
    },
    onSuccess: (response: LoginResponse) => {
      const { user, access_token, refresh_token } = response
      
      // Update auth store
      useAuthStore.setState({
        user,
        token: access_token,
        refreshToken: refresh_token,
        isLoading: false,
        error: null,
      })
      
      // Store tokens in localStorage
      localStorage.setItem(config.auth.tokenKey, access_token)
      localStorage.setItem(config.auth.refreshTokenKey, refresh_token)
      
      // Set user data in React Query cache
      queryClient.setQueryData(authKeys.me(), user)
      
      // Show success notification
      useAppStore.getState().addNotification({
        type: 'success',
        title: 'Bienvenido',
        message: `Hola ${user.display_name || user.email}`,
        duration: 3000,
      })
      
      // Navigate to dashboard
      navigate('/app/dashboard')
    },
    onError: (error: any) => {
      const errorMessage = error?.message || 'Error al iniciar sesión'
      
      // Update auth store with error
      useAuthStore.setState({
        isLoading: false,
        error: errorMessage,
      })
      
      // Show error notification
      useAppStore.getState().addNotification({
        type: 'error',
        title: 'Error de autenticación',
        message: errorMessage,
        duration: 5000,
      })
    },
  })
}

/**
 * Hook for register mutation with proper error handling
 */
export const useRegister = () => {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  
  return useMutation({
    mutationFn: authService.register,
    onMutate: () => {
      // Clear any existing auth errors
      useAuthStore.getState().clearError()
      // Set loading state
      useAuthStore.setState({ isLoading: true })
    },
    onSuccess: (response: RegisterResponse) => {
      const { user, access_token, refresh_token } = response
      
      // Update auth store
      useAuthStore.setState({
        user,
        token: access_token,
        refreshToken: refresh_token,
        isLoading: false,
        error: null,
      })
      
      // Store tokens in localStorage
      localStorage.setItem(config.auth.tokenKey, access_token)
      localStorage.setItem(config.auth.refreshTokenKey, refresh_token)
      
      // Set user data in React Query cache
      queryClient.setQueryData(authKeys.me(), user)
      
      // Show success notification
      useAppStore.getState().addNotification({
        type: 'success',
        title: 'Cuenta creada',
        message: `Bienvenido ${user.display_name || user.email}`,
        duration: 3000,
      })
      
      // Navigate to dashboard
      navigate('/app/dashboard')
    },
    onError: (error: any) => {
      const errorMessage = error?.message || 'Error al registrarse'
      
      // Update auth store with error
      useAuthStore.setState({
        isLoading: false,
        error: errorMessage,
      })
      
      // Show error notification
      useAppStore.getState().addNotification({
        type: 'error',
        title: 'Error de registro',
        message: errorMessage,
        duration: 5000,
      })
    },
  })
}

/**
 * Hook for logout mutation with proper cleanup
 */
export const useLogout = () => {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  
  return useMutation({
    mutationFn: authService.logout,
    onMutate: () => {
      // Immediately clear auth state for better UX
      useAuthStore.getState().logout()
      
      // Clear all React Query cache
      queryClient.clear()
      
      // Navigate to login
      navigate('/auth/login')
    },
    onError: (error) => {
      // Even if logout API call fails, we still want to clear local state
      console.warn('Logout API call failed:', error)
      
      // Show warning notification
      useAppStore.getState().addNotification({
        type: 'warning',
        title: 'Sesión cerrada',
        message: 'Tu sesión ha sido cerrada localmente',
        duration: 3000,
      })
    },
    onSuccess: () => {
      // Show success notification
      useAppStore.getState().addNotification({
        type: 'success',
        title: 'Sesión cerrada',
        message: 'Has cerrado sesión correctamente',
        duration: 3000,
      })
    },
  })
}

/**
 * Hook for profile update mutation with optimistic updates
 */
export const useUpdateProfile = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: authService.updateProfile,
    onMutate: async (newData: ProfileUpdateData) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: authKeys.me() })
      
      // Snapshot the previous value
      const previousUser = queryClient.getQueryData<User>(authKeys.me())
      
      // Optimistically update the cache
      if (previousUser) {
        const optimisticUser = { ...previousUser, ...newData }
        queryClient.setQueryData(authKeys.me(), optimisticUser)
        
        // Also update the auth store for immediate UI updates
        useAuthStore.getState().updateUser(newData)
      }
      
      // Return context with previous data for rollback
      return { previousUser }
    },
    onError: (error: any, newData, context) => {
      // Rollback optimistic update
      if (context?.previousUser) {
        queryClient.setQueryData(authKeys.me(), context.previousUser)
        useAuthStore.getState().setUser(context.previousUser)
      }
      
      // Show error notification
      useAppStore.getState().addNotification({
        type: 'error',
        title: 'Error al actualizar perfil',
        message: error?.message || 'No se pudo actualizar el perfil',
        duration: 5000,
      })
    },
    onSuccess: (updatedUser: User) => {
      // Update auth store with server response
      useAuthStore.getState().setUser(updatedUser)
      
      // Show success notification
      useAppStore.getState().addNotification({
        type: 'success',
        title: 'Perfil actualizado',
        message: 'Tu perfil ha sido actualizado correctamente',
        duration: 3000,
      })
    },
    onSettled: () => {
      // Always refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: authKeys.me() })
    },
  })
}

/**
 * Hook for password change mutation
 */
export const useChangePassword = () => {
  return useMutation({
    mutationFn: authService.changePassword,
    onSuccess: () => {
      // Show success notification
      useAppStore.getState().addNotification({
        type: 'success',
        title: 'Contraseña actualizada',
        message: 'Tu contraseña ha sido cambiada correctamente',
        duration: 3000,
      })
    },
    onError: (error: any) => {
      // Show error notification
      useAppStore.getState().addNotification({
        type: 'error',
        title: 'Error al cambiar contraseña',
        message: error?.message || 'No se pudo cambiar la contraseña',
        duration: 5000,
      })
    },
  })
}

/**
 * Hook for token refresh with proper error handling
 * This is typically called automatically by the API client
 */
export const useRefreshToken = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (refreshToken: string) => authService.refreshToken(refreshToken),
    onSuccess: (response) => {
      const { access_token, refresh_token } = response
      
      // Update auth store
      useAuthStore.setState({
        token: access_token,
        refreshToken: refresh_token,
      })
      
      // Update tokens in localStorage
      localStorage.setItem(config.auth.tokenKey, access_token)
      localStorage.setItem(config.auth.refreshTokenKey, refresh_token)
    },
    onError: (error) => {
      console.error('Token refresh failed:', error)
      
      // If refresh fails, logout user
      useAuthStore.getState().logout()
      queryClient.clear()
      
      // Show error notification
      useAppStore.getState().addNotification({
        type: 'error',
        title: 'Sesión expirada',
        message: 'Tu sesión ha expirado. Por favor, inicia sesión nuevamente.',
        duration: 5000,
      })
      
      // Redirect to login
      window.location.href = '/auth/login'
    },
  })
}

/**
 * Hook for forgot password mutation
 */
export const useForgotPassword = () => {
  return useMutation({
    mutationFn: (email: string) => authService.forgotPassword({ email }),
    onSuccess: () => {
      useAppStore.getState().addNotification({
        type: 'success',
        title: 'Email enviado',
        message: 'Se ha enviado un enlace de recuperación a tu email',
        duration: 5000,
      })
    },
    onError: (error: any) => {
      useAppStore.getState().addNotification({
        type: 'error',
        title: 'Error',
        message: error?.message || 'No se pudo enviar el email de recuperación',
        duration: 5000,
      })
    },
  })
}

/**
 * Hook for reset password mutation
 */
export const useResetPassword = () => {
  const navigate = useNavigate()
  
  return useMutation({
    mutationFn: authService.resetPassword,
    onSuccess: () => {
      useAppStore.getState().addNotification({
        type: 'success',
        title: 'Contraseña restablecida',
        message: 'Tu contraseña ha sido restablecida correctamente',
        duration: 3000,
      })
      
      // Navigate to login
      navigate('/auth/login')
    },
    onError: (error: any) => {
      useAppStore.getState().addNotification({
        type: 'error',
        title: 'Error',
        message: error?.message || 'No se pudo restablecer la contraseña',
        duration: 5000,
      })
    },
  })
}

/**
 * Hook for email verification
 */
export const useVerifyEmail = () => {
  return useMutation({
    mutationFn: authService.verifyEmail,
    onSuccess: () => {
      useAppStore.getState().addNotification({
        type: 'success',
        title: 'Email verificado',
        message: 'Tu email ha sido verificado correctamente',
        duration: 3000,
      })
    },
    onError: (error: any) => {
      useAppStore.getState().addNotification({
        type: 'error',
        title: 'Error de verificación',
        message: error?.message || 'No se pudo verificar el email',
        duration: 5000,
      })
    },
  })
}

/**
 * Hook for resending email verification
 */
export const useResendVerification = () => {
  return useMutation({
    mutationFn: (email: string) => authService.resendVerification(email),
    onSuccess: () => {
      useAppStore.getState().addNotification({
        type: 'success',
        title: 'Email enviado',
        message: 'Se ha enviado un nuevo email de verificación',
        duration: 3000,
      })
    },
    onError: (error: any) => {
      useAppStore.getState().addNotification({
        type: 'error',
        title: 'Error',
        message: error?.message || 'No se pudo enviar el email de verificación',
        duration: 5000,
      })
    },
  })
}