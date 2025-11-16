import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate, useLocation } from 'react-router-dom'
import { authService } from '@/services/authService'
import { authKeys, queryKeyUtils } from '@/lib/queryKeys'
import { useAuthStore } from '@/store/auth'
import { showToast } from '@/lib/toast'
import { config, routes } from '@/lib/config'
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
  const location = useLocation()
  
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

      // Navigate immediately - don't wait
      const from = (location.state as any)?.from || routes.app.dashboard
      navigate(from, { replace: true })

      // Show success notification AFTER navigation
      // This ensures the toast appears on the new page
      setTimeout(() => {
        showToast.success('Bienvenido', `Hola ${user.display_name || user.email}`, { duration: 2500 })
      }, 100)
    },
    onError: (error: any) => {
      // Extract error message from various possible structures
      let errorMessage = 'Error al iniciar sesión'

      if (typeof error === 'string') {
        errorMessage = error
      } else if (error?.message) {
        errorMessage = String(error.message)
      } else if (error?.detail) {
        errorMessage = String(error.detail)
      } else if (error?.error) {
        errorMessage = String(error.error)
      }

      // Ensure it's always a string (handle edge cases)
      errorMessage = String(errorMessage)

      // Map common backend error messages to user-friendly Spanish
      if (errorMessage === 'Invalid credentials') {
        errorMessage = 'Credenciales inválidas. Verifica tu email y contraseña.'
      } else if (errorMessage.toLowerCase().includes('user not found') || errorMessage.toLowerCase().includes('usuario no encontrado')) {
        errorMessage = 'No existe una cuenta con ese email.'
      }

      console.log('[Login Error]', { originalError: error, extractedMessage: errorMessage })

      // Update auth store with error
      useAuthStore.setState({
        isLoading: false,
        error: errorMessage,
      })

      // Show error notification
      showToast.error('Error de autenticación', errorMessage)
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

      // Navigate immediately
      navigate(routes.app.dashboard, { replace: true })

      // Show success notification AFTER navigation
      setTimeout(() => {
        showToast.success('Cuenta creada', `Bienvenido ${user.display_name || user.email}`, { duration: 2500 })
      }, 100)
    },
    onError: (error: any) => {
      // Extract error message from various possible structures
      let errorMessage = 'Error al registrarse'

      if (typeof error === 'string') {
        errorMessage = error
      } else if (error?.message) {
        errorMessage = String(error.message)
      } else if (error?.detail) {
        errorMessage = String(error.detail)
      } else if (error?.error) {
        errorMessage = String(error.error)
      }

      // Ensure it's always a string (handle edge cases)
      errorMessage = String(errorMessage)

      // Map common backend error messages to user-friendly Spanish
      if (errorMessage.toLowerCase().includes('already exists') || errorMessage.toLowerCase().includes('ya existe')) {
        errorMessage = 'Ya existe una cuenta con ese email.'
      } else if (errorMessage.toLowerCase().includes('invalid email')) {
        errorMessage = 'Email inválido.'
      } else if (errorMessage.toLowerCase().includes('password')) {
        errorMessage = 'La contraseña debe tener al menos 8 caracteres.'
      }

      console.log('[Register Error]', { originalError: error, extractedMessage: errorMessage })

      // Update auth store with error
      useAuthStore.setState({
        isLoading: false,
        error: errorMessage,
      })

      // Show error notification
      showToast.error('Error de registro', errorMessage)
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
    onSuccess: () => {
      // Clear auth state
      useAuthStore.getState().logout()

      // Clear all React Query cache
      queryClient.clear()

      // Navigate to login
      navigate('/auth/login')

      // Show logout notification AFTER navigation
      // This ensures the toast appears on the login page
      setTimeout(() => {
        showToast.success('Sesión cerrada', 'Has cerrado sesión correctamente')
      }, 100)
    },
    onError: (error) => {
      // Even if logout API call fails, we still want to clear local state
      console.warn('Logout API call failed:', error)

      // Clear auth state anyway
      useAuthStore.getState().logout()
      queryClient.clear()

      // Navigate to login
      navigate('/auth/login')

      // Show warning notification AFTER navigation
      setTimeout(() => {
        showToast.warning('Sesión cerrada', 'Tu sesión ha sido cerrada localmente')
      }, 100)
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
      showToast.error('Error al actualizar perfil', error?.message || 'No se pudo actualizar el perfil')
    },
    onSuccess: (updatedUser: User) => {
      // Update auth store with server response
      useAuthStore.getState().setUser(updatedUser)
      
      // Show success notification
      showToast.success('Perfil actualizado', 'Tu perfil ha sido actualizado correctamente')
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
      showToast.success('Contraseña actualizada', 'Tu contraseña ha sido cambiada correctamente')
    },
    onError: (error: any) => {
      // Show error notification
      showToast.error('Error al cambiar contraseña', error?.message || 'No se pudo cambiar la contraseña')
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
      showToast.error('Sesión expirada', 'Tu sesión ha expirado. Por favor, inicia sesión nuevamente.')
      
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
      showToast.success('Email enviado', 'Se ha enviado un enlace de recuperación a tu email', { duration: 5000 })
    },
    onError: (error: any) => {
      showToast.error('Error', error?.message || 'No se pudo enviar el email de recuperación')
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
      showToast.success('Contraseña restablecida', 'Tu contraseña ha sido restablecida correctamente')

      // Navigate to login
      navigate('/auth/login')
    },
    onError: (error: any) => {
      showToast.error('Error', error?.message || 'No se pudo restablecer la contraseña')
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
      showToast.success('Email verificado', 'Tu email ha sido verificado correctamente')
    },
    onError: (error: any) => {
      showToast.error('Error de verificación', error?.message || 'No se pudo verificar el email')
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
      showToast.success('Email enviado', 'Se ha enviado un nuevo email de verificación')
    },
    onError: (error: any) => {
      showToast.error('Error', error?.message || 'No se pudo enviar el email de verificación')
    },
  })
}