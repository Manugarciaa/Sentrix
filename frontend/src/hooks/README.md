# Error Handling and Network Recovery Hooks

This directory contains comprehensive error handling and network recovery utilities for the Sentrix frontend application.

## Overview

The error handling system provides:
- **Global mutation error handling** with automatic token refresh
- **Network recovery utilities** for handling online/offline states
- **User-friendly error messages** based on error types
- **Automatic retry logic** for recoverable errors
- **Request deduplication** and cancellation

## Core Hooks

### `useGlobalMutationDefaults`

Provides consistent error handling across all mutations with automatic token refresh on 401 errors.

```typescript
import { useGlobalMutationDefaults } from '@/hooks/useGlobalMutationDefaults'

const updateProfile = useMutation({
  ...useGlobalMutationDefaults('actualizar perfil', {
    showSuccessNotification: true,
    successMessage: 'Perfil actualizado correctamente'
  }),
  mutationFn: authService.updateProfile,
})
```

### `useAuthenticatedMutationDefaults`

Specialized version for mutations that require authentication, with automatic token refresh.

```typescript
import { useAuthenticatedMutationDefaults } from '@/hooks/useGlobalMutationDefaults'

const createUser = useMutation({
  ...useAuthenticatedMutationDefaults('crear usuario'),
  mutationFn: userService.createUser,
})
```

### `useNetworkRecovery`

Monitors network status and handles automatic recovery when connection is restored.

```typescript
import { useNetworkRecovery } from '@/hooks/useNetworkRecovery'

const { 
  isOnline, 
  isSlowConnection, 
  retryFailedOperations 
} = useNetworkRecovery({
  enableNotifications: true,
  enableAutoRetry: true,
  onOnline: () => console.log('Network recovered'),
  onOffline: () => console.log('Network lost')
})
```

## Error Classification

The system automatically classifies errors into types for appropriate handling:

- **NETWORK**: Connection issues, fetch failures
- **AUTHENTICATION**: 401 errors, expired tokens
- **AUTHORIZATION**: 403 errors, insufficient permissions
- **VALIDATION**: 400-499 client errors
- **SERVER**: 500+ server errors
- **TIMEOUT**: Request cancellation, timeouts

## Features

### Automatic Token Refresh

When a 401 error occurs, the system automatically:
1. Attempts to refresh the access token
2. Retries the original request with the new token
3. If refresh fails, logs out the user and redirects to login

### Network Recovery

The system monitors network status and:
- Shows notifications when going offline/online
- Automatically resumes paused mutations when online
- Detects slow connections and adjusts behavior
- Provides retry mechanisms for failed operations

### User-Friendly Messages

Error messages are automatically translated to user-friendly Spanish messages:
- Network errors: "No se pudo conectar con el servidor..."
- Auth errors: "Tu sesión ha expirado..."
- Server errors: "Error interno del servidor..."
- Validation errors: Uses server message when available

## Migration Guide

### Before (Manual Error Handling)

```typescript
const updateUser = useMutation({
  mutationFn: userService.updateUser,
  onError: (error: any) => {
    if (error.status === 401) {
      // Manual auth handling
      window.location.href = '/login'
    } else if (error.status >= 500) {
      // Manual server error handling
      toast.error('Server error occurred')
    }
    // ... more manual handling
  },
  onSuccess: () => {
    toast.success('User updated successfully')
  }
})
```

### After (Global Error Handling)

```typescript
const updateUser = useMutation({
  ...useAuthenticatedMutationDefaults('actualizar usuario', {
    showSuccessNotification: true,
    successMessage: 'Usuario actualizado correctamente'
  }),
  mutationFn: userService.updateUser,
  // Only custom business logic needed
  onSuccess: (data) => {
    console.log('User updated:', data)
  }
})
```

## Error Boundary Integration

Wrap your app or components with the NetworkErrorBoundary for handling network-related crashes:

```typescript
import { NetworkErrorBoundary } from '@/hooks/useNetworkRecovery'

function App() {
  return (
    <NetworkErrorBoundary
      fallback={({ error, retry }) => (
        <ErrorFallback error={error} onRetry={retry} />
      )}
    >
      <YourApp />
    </NetworkErrorBoundary>
  )
}
```

## Testing

The system includes utilities for testing error scenarios:

```typescript
import { mockNetworkError, mockAuthError } from '@/hooks/examples/errorHandlingIntegration.example'

test('handles network errors', async () => {
  const restoreFetch = mockNetworkError()
  
  // Test your component/hook
  
  restoreFetch()
})
```

## Best Practices

1. **Use global defaults**: Apply `useAuthenticatedMutationDefaults` to all authenticated mutations
2. **Custom logic only**: Only add custom `onSuccess`/`onError` handlers for business logic
3. **Network monitoring**: Use `useNetworkRecovery` in components that need network awareness
4. **Error boundaries**: Wrap critical sections with `NetworkErrorBoundary`
5. **Testing**: Test error scenarios using the provided mock utilities

## Configuration

The error handling system respects these configuration options:

```typescript
// Global mutation defaults options
{
  showSuccessNotification?: boolean    // Show success toast
  successMessage?: string             // Custom success message
  enableAutoRetry?: boolean          // Enable automatic retries
  retryCondition?: (error) => boolean // Custom retry logic
}

// Network recovery options
{
  enableNotifications?: boolean       // Show network status notifications
  enableAutoRetry?: boolean          // Auto-retry failed operations
  retryDelay?: number               // Delay between retries (ms)
  maxRetries?: number               // Maximum retry attempts
  onOnline?: () => void             // Custom online handler
  onOffline?: () => void            // Custom offline handler
  onSlowConnection?: () => void     // Custom slow connection handler
}
```

## Error Types Reference

| Error Type | Status Codes | Behavior |
|------------|--------------|----------|
| NETWORK | - | Show warning, enable retry |
| AUTHENTICATION | 401 | Auto token refresh, redirect if failed |
| AUTHORIZATION | 403 | Show error, no retry |
| VALIDATION | 400-499 | Show server message, no retry |
| SERVER | 500+ | Show error, enable retry |
| TIMEOUT | - | Silent handling, enable retry |

## Examples

See `frontend/src/hooks/examples/errorHandlingIntegration.example.ts` for comprehensive usage examples.