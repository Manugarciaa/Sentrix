/**
 * EXAMPLE: Integration of Global Error Handling and Network Recovery
 * 
 * This file demonstrates how to integrate the new error handling and network recovery
 * utilities with existing React Query mutations and components.
 * 
 * DO NOT IMPORT THIS FILE IN PRODUCTION CODE - IT'S FOR REFERENCE ONLY
 */

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuthenticatedMutationDefaults, createMutationOptions } from '@/hooks/useGlobalMutationDefaults'
import { useNetworkRecovery, NetworkErrorBoundary } from '@/hooks/useNetworkRecovery'
import { authService } from '@/services/authService'
import { userService } from '@/services/userService'

// ============================================================================
// EXAMPLE 1: Simple mutation with global error handling
// ============================================================================

export const useSimpleProfileUpdate = () => {
  return useMutation({
    // Apply global error handling defaults for authenticated operations
    ...useAuthenticatedMutationDefaults('actualizar perfil', {
      showSuccessNotification: true,
      successMessage: 'Perfil actualizado correctamente'
    }),
    mutationFn: authService.updateProfile,
    // Custom logic can still be added
    onSuccess: (data) => {
      console.log('Profile updated:', data)
      // Global success notification will be shown automatically
    },
    onError: (error) => {
      console.error('Profile update failed:', error)
      // Global error handling will show appropriate notification
      // and handle token refresh if needed
    }
  })
}

// ============================================================================
// EXAMPLE 2: Complex mutation with optimistic updates and global error handling
// ============================================================================

export const useAdvancedUserUpdate = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    // Use the createMutationOptions helper for more control
    ...createMutationOptions(
      ({ id, data }: { id: string; data: any }) => userService.updateUser(id, data),
      'actualizar usuario',
      {
        showSuccessNotification: true,
        successMessage: 'Usuario actualizado correctamente',
        requiresAuth: true,
        onSuccess: (data, variables) => {
          // Custom success logic
          console.log(`User ${variables.id} updated successfully`)
        },
        onError: (error, variables) => {
          // Custom error logic (runs after global error handling)
          console.error(`Failed to update user ${variables.id}:`, error)
        }
      }
    ),
    
    // Optimistic updates
    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({ queryKey: ['users', id] })
      const previousUser = queryClient.getQueryData(['users', id])
      
      if (previousUser) {
        queryClient.setQueryData(['users', id], { ...previousUser, ...data })
      }
      
      return { previousUser }
    },
    
    // Rollback on error (global error handling will show notification)
    onError: (error, variables, context) => {
      if (context?.previousUser) {
        queryClient.setQueryData(['users', variables.id], context.previousUser)
      }
    },
    
    onSettled: (data, error, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['users', id] })
    }
  })
}

// ============================================================================
// EXAMPLE 3: Component with network recovery integration
// ============================================================================

export const ExampleComponentWithNetworkRecovery: React.FC = () => {
  // Monitor network status and handle recovery
  const { 
    isOnline, 
    isSlowConnection, 
    retryFailedOperations, 
    canRetry 
  } = useNetworkRecovery({
    enableNotifications: true,
    enableAutoRetry: true,
    onOnline: () => {
      console.log('Network recovered - refreshing data')
    },
    onOffline: () => {
      console.log('Network lost - operations will be queued')
    },
    onSlowConnection: () => {
      console.log('Slow connection detected - optimizing requests')
    }
  })

  const updateProfile = useSimpleProfileUpdate()

  const handleUpdateProfile = async (data: any) => {
    if (!isOnline) {
      // Could queue the operation for when network returns
      console.log('Offline - operation will be queued')
      return
    }

    try {
      await updateProfile.mutateAsync(data)
    } catch (error) {
      // Global error handling will manage the error
      // Custom error logic can go here if needed
    }
  }

  return (
    <div>
      {/* Network status indicator */}
      {!isOnline && (
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-4">
          <p>Sin conexión - Las operaciones se reanudarán automáticamente</p>
          {canRetry && (
            <button 
              onClick={retryFailedOperations}
              className="mt-2 bg-yellow-500 text-white px-3 py-1 rounded text-sm"
            >
              Reintentar ahora
            </button>
          )}
        </div>
      )}

      {isSlowConnection && (
        <div className="bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded mb-4">
          <p>Conexión lenta detectada - Las operaciones pueden tardar más</p>
        </div>
      )}

      {/* Your component content */}
      <button
        onClick={() => handleUpdateProfile({ name: 'New Name' })}
        disabled={updateProfile.isPending || !isOnline}
        className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
      >
        {updateProfile.isPending ? 'Actualizando...' : 'Actualizar Perfil'}
      </button>
    </div>
  )
}

// ============================================================================
// EXAMPLE 4: App-level integration with error boundaries
// ============================================================================

export const AppWithErrorBoundaries: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <NetworkErrorBoundary
      fallback={({ error, retry }) => (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
            <div className="flex items-center mb-4">
              <div className="flex-shrink-0">
                <svg className="h-8 w-8 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-gray-800">
                  Error de conexión
                </h3>
              </div>
            </div>
            <div className="mb-4">
              <p className="text-sm text-gray-600">
                No se pudo conectar con el servidor. Verifica tu conexión a internet e intenta nuevamente.
              </p>
            </div>
            <div className="flex justify-end">
              <button
                onClick={retry}
                className="bg-blue-600 text-white px-4 py-2 text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                Reintentar
              </button>
            </div>
          </div>
        </div>
      )}
      onError={(error, errorInfo) => {
        // Log error to monitoring service
        console.error('Network Error Boundary:', error, errorInfo)
      }}
    >
      {children}
    </NetworkErrorBoundary>
  )
}

// ============================================================================
// EXAMPLE 5: Migration guide for existing mutations
// ============================================================================

// BEFORE: Manual error handling
const useOldStyleMutation = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: userService.createUser,
    onError: (error: any) => {
      // Manual error handling
      if (error.status === 401) {
        // Handle auth error manually
        window.location.href = '/login'
      } else if (error.status >= 500) {
        // Handle server error manually
        alert('Server error occurred')
      } else {
        // Handle other errors manually
        alert(error.message || 'An error occurred')
      }
    },
    onSuccess: () => {
      // Manual success notification
      alert('User created successfully')
    }
  })
}

// AFTER: Using global error handling
const useNewStyleMutation = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    // Global error handling with automatic token refresh, 
    // user-friendly notifications, and network recovery
    ...useAuthenticatedMutationDefaults('crear usuario', {
      showSuccessNotification: true,
      successMessage: 'Usuario creado correctamente'
    }),
    mutationFn: userService.createUser,
    // Only custom logic needed now
    onSuccess: (data) => {
      // Custom business logic only
      console.log('User created:', data)
      queryClient.invalidateQueries({ queryKey: ['users'] })
    }
  })
}

// ============================================================================
// EXAMPLE 6: Testing with the new error handling
// ============================================================================

// Test helper for mocking network errors
export const mockNetworkError = () => {
  const originalFetch = global.fetch
  global.fetch = jest.fn(() => Promise.reject(new Error('Network error')))
  return () => { global.fetch = originalFetch }
}

// Test helper for mocking auth errors
export const mockAuthError = () => {
  const originalFetch = global.fetch
  global.fetch = jest.fn(() => Promise.resolve({
    ok: false,
    status: 401,
    json: () => Promise.resolve({ message: 'Unauthorized' })
  }))
  return () => { global.fetch = originalFetch }
}

// Example test
/*
describe('useSimpleProfileUpdate', () => {
  it('should handle network errors gracefully', async () => {
    const restoreFetch = mockNetworkError()
    
    const { result } = renderHook(() => useSimpleProfileUpdate())
    
    act(() => {
      result.current.mutate({ name: 'Test' })
    })
    
    await waitFor(() => {
      expect(result.current.isError).toBe(true)
    })
    
    // Verify that global error handling showed appropriate notification
    expect(screen.getByText(/error de conexión/i)).toBeInTheDocument()
    
    restoreFetch()
  })
})
*/

export default {
  useSimpleProfileUpdate,
  useAdvancedUserUpdate,
  ExampleComponentWithNetworkRecovery,
  AppWithErrorBoundaries,
  useOldStyleMutation,
  useNewStyleMutation,
}