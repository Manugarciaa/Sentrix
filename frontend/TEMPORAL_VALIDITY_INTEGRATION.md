# Integración de Validez Temporal en Frontend
# Temporal Validity Integration in Frontend

## Descripción General / Overview

El sistema de validez temporal permite rastrear y gestionar la validez de las detecciones de criaderos en función del tiempo. No todos los criaderos persisten de la misma manera:

- **Charcos**: Se secan en horas/días dependiendo del clima
- **Basura**: Puede ser recogida en días/semanas
- **Baches**: Persisten semanas a meses
- **Calles rotas**: Requieren reparación estructural (meses a años)

## API Endpoints Disponibles

### 1. Obtener Detecciones Expiradas

```typescript
GET /api/v1/detections/expired
Query Parameters:
  - limit: number (default: 50, max: 500)
  - offset: number (default: 0)
  - breeding_site_type?: string (opcional)

Response: DetectionWithValidity[]
```

**Ejemplo de uso:**

```typescript
import { apiClient } from '@/api/client'

async function getExpiredDetections(limit = 50, offset = 0) {
  const response = await apiClient.get('/api/v1/detections/expired', {
    params: { limit, offset }
  })
  return response.data
}
```

### 2. Obtener Detecciones Por Expirar

```typescript
GET /api/v1/detections/expiring-soon
Query Parameters:
  - days_threshold: number (default: 1, max: 30)
  - limit: number (default: 50, max: 500)
  - offset: number (default: 0)

Response: DetectionWithValidity[]
```

**Ejemplo de uso:**

```typescript
async function getExpiringSoon(daysThreshold = 1) {
  const response = await apiClient.get('/api/v1/detections/expiring-soon', {
    params: { days_threshold: daysThreshold, limit: 100 }
  })
  return response.data
}
```

### 3. Extender Validez de Detección

```typescript
POST /api/v1/detections/extend-validity
Body: {
  detection_id: string
  extension_days: number (1-365)
  reason: string (max 500 chars)
}

Response: ValidityExtensionResponse
```

**Ejemplo de uso:**

```typescript
async function extendDetectionValidity(
  detectionId: string,
  extensionDays: number,
  reason: string
) {
  const response = await apiClient.post('/api/v1/detections/extend-validity', {
    detection_id: detectionId,
    extension_days: extensionDays,
    reason
  })
  return response.data
}
```

### 4. Revalidar Detección

```typescript
POST /api/v1/detections/{detection_id}/revalidate
Query Parameters:
  - weather_condition?: string (SUNNY, RAINY, CLOUDY, DRY_SEASON, WET_SEASON)

Response: {
  detection_id: string
  status: "revalidated"
  validated_by: string
  validated_at: string
  validity_period_days: number
  expires_at: string
  validity_status: ValidityStatus
}
```

**Ejemplo de uso:**

```typescript
async function revalidateDetection(
  detectionId: string,
  weatherCondition?: string
) {
  const response = await apiClient.post(
    `/api/v1/detections/${detectionId}/revalidate`,
    null,
    { params: { weather_condition: weatherCondition } }
  )
  return response.data
}
```

### 5. Obtener Estadísticas de Validez

```typescript
GET /api/v1/detections/validity-stats

Response: {
  total_detections: number
  active_detections: number
  expired_detections: number
  expiring_soon_detections: number
  by_persistence_type: Record<string, number>
  by_breeding_site: Record<string, number>
  average_validity_days: number
  revalidation_needed: number
}
```

**Ejemplo de uso:**

```typescript
async function getValidityStatistics() {
  const response = await apiClient.get('/api/v1/detections/validity-stats')
  return response.data
}
```

### 6. Obtener Estado de Validez de una Detección

```typescript
GET /api/v1/detections/{detection_id}/validity

Response: {
  is_expired: boolean
  is_expiring_soon: boolean
  remaining_days: number | null
  status: "VALID" | "MEDIUM_VALIDITY" | "LOW_VALIDITY" | "EXPIRING_SOON" | "EXPIRED"
  validity_percentage: number
  requires_revalidation: boolean
}
```

## Tipos TypeScript

```typescript
// frontend/src/types/validity.ts

export enum PersistenceType {
  TRANSIENT = "TRANSIENT",       // Horas a días
  SHORT_TERM = "SHORT_TERM",     // Días a semanas
  MEDIUM_TERM = "MEDIUM_TERM",   // Semanas a meses
  LONG_TERM = "LONG_TERM",       // Meses a años
  PERMANENT = "PERMANENT"        // Permanente
}

export enum ValidityStatusType {
  VALID = "VALID",
  MEDIUM_VALIDITY = "MEDIUM_VALIDITY",
  LOW_VALIDITY = "LOW_VALIDITY",
  EXPIRING_SOON = "EXPIRING_SOON",
  EXPIRED = "EXPIRED"
}

export interface ValidityStatus {
  is_expired: boolean
  is_expiring_soon: boolean
  remaining_days: number | null
  status: ValidityStatusType
  validity_percentage: number
  requires_revalidation: boolean
}

export interface DetectionWithValidity {
  id: string
  analysis_id: string
  class_name: string
  confidence: number
  risk_level: string
  breeding_site_type: string
  persistence_type: PersistenceType | null
  validity_period_days: number | null
  expires_at: string | null
  is_weather_dependent: boolean
  validity_status: ValidityStatus | null
  created_at: string
}

export interface ValidityExtensionRequest {
  detection_id: string
  extension_days: number
  reason: string
}

export interface ValidityStatistics {
  total_detections: number
  active_detections: number
  expired_detections: number
  expiring_soon_detections: number
  by_persistence_type: Record<string, number>
  by_breeding_site: Record<string, number>
  average_validity_days: number
  revalidation_needed: number
}
```

## Componentes UI Recomendados

### 1. Badge de Estado de Validez

```tsx
// frontend/src/components/ui/ValidityBadge.tsx

import { Badge } from '@/components/ui/Badge'
import { ValidityStatus } from '@/types/validity'

interface ValidityBadgeProps {
  status: ValidityStatus
}

export function ValidityBadge({ status }: ValidityBadgeProps) {
  const getVariant = () => {
    if (status.is_expired) return 'destructive'
    if (status.is_expiring_soon) return 'warning'
    if (status.validity_percentage < 50) return 'secondary'
    return 'success'
  }

  const getLabel = () => {
    if (status.is_expired) return 'Expirada'
    if (status.is_expiring_soon) return 'Por expirar'
    if (status.remaining_days !== null) {
      return `${status.remaining_days}d restantes`
    }
    return 'Válida'
  }

  return (
    <Badge variant={getVariant()}>
      {getLabel()}
    </Badge>
  )
}
```

### 2. Barra de Progreso de Validez

```tsx
// frontend/src/components/ui/ValidityProgressBar.tsx

import { ProgressBar } from '@/components/ui/ProgressBar'
import { ValidityStatus } from '@/types/validity'

interface ValidityProgressBarProps {
  status: ValidityStatus
  showLabel?: boolean
}

export function ValidityProgressBar({
  status,
  showLabel = true
}: ValidityProgressBarProps) {
  const getColor = () => {
    if (status.validity_percentage >= 70) return 'success'
    if (status.validity_percentage >= 40) return 'warning'
    return 'danger'
  }

  return (
    <div className="w-full">
      <ProgressBar
        value={status.validity_percentage}
        color={getColor()}
      />
      {showLabel && (
        <p className="text-sm text-gray-600 mt-1">
          {status.remaining_days !== null
            ? `${status.remaining_days} días restantes`
            : 'Sin expiración'}
        </p>
      )}
    </div>
  )
}
```

### 3. Diálogo de Extensión de Validez

```tsx
// frontend/src/components/domain/ExtendValidityDialog.tsx

import { useState } from 'react'
import { Dialog } from '@/components/ui/Dialog'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { extendDetectionValidity } from '@/services/detections'

interface ExtendValidityDialogProps {
  detectionId: string
  currentExpiresAt: string
  onSuccess: () => void
  onClose: () => void
}

export function ExtendValidityDialog({
  detectionId,
  currentExpiresAt,
  onSuccess,
  onClose
}: ExtendValidityDialogProps) {
  const [extensionDays, setExtensionDays] = useState(7)
  const [reason, setReason] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    setLoading(true)
    try {
      await extendDetectionValidity(detectionId, extensionDays, reason)
      onSuccess()
      onClose()
    } catch (error) {
      console.error('Error extending validity:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open onClose={onClose}>
      <Dialog.Title>Extender Validez de Detección</Dialog.Title>

      <div className="space-y-4 mt-4">
        <div>
          <label className="block text-sm font-medium mb-1">
            Días de extensión
          </label>
          <Input
            type="number"
            min={1}
            max={365}
            value={extensionDays}
            onChange={(e) => setExtensionDays(Number(e.target.value))}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            Razón de extensión
          </label>
          <textarea
            className="w-full border rounded p-2"
            rows={3}
            maxLength={500}
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Explique por qué se necesita extender la validez..."
          />
        </div>

        <div className="text-sm text-gray-600">
          <p>Expiración actual: {new Date(currentExpiresAt).toLocaleDateString()}</p>
          <p className="font-medium">
            Nueva expiración: {new Date(
              new Date(currentExpiresAt).getTime() + extensionDays * 24 * 60 * 60 * 1000
            ).toLocaleDateString()}
          </p>
        </div>
      </div>

      <Dialog.Actions>
        <Button variant="outline" onClick={onClose}>
          Cancelar
        </Button>
        <Button
          onClick={handleSubmit}
          disabled={loading || !reason.trim()}
        >
          {loading ? 'Extendiendo...' : 'Extender Validez'}
        </Button>
      </Dialog.Actions>
    </Dialog>
  )
}
```

## Hooks Personalizados

### useDetectionValidity

```typescript
// frontend/src/hooks/useDetectionValidity.ts

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/api/client'
import { ValidityStatus } from '@/types/validity'

export function useDetectionValidity(detectionId: string) {
  return useQuery({
    queryKey: ['detection-validity', detectionId],
    queryFn: async () => {
      const response = await apiClient.get<ValidityStatus>(
        `/api/v1/detections/${detectionId}/validity`
      )
      return response.data
    },
    refetchInterval: 60000, // Refetch every minute
  })
}
```

### useExpiredDetections

```typescript
// frontend/src/hooks/useExpiredDetections.ts

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/api/client'
import { DetectionWithValidity } from '@/types/validity'

export function useExpiredDetections(limit = 50, offset = 0) {
  return useQuery({
    queryKey: ['expired-detections', limit, offset],
    queryFn: async () => {
      const response = await apiClient.get<DetectionWithValidity[]>(
        '/api/v1/detections/expired',
        { params: { limit, offset } }
      )
      return response.data
    },
  })
}
```

### useValidityStatistics

```typescript
// frontend/src/hooks/useValidityStatistics.ts

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/api/client'
import { ValidityStatistics } from '@/types/validity'

export function useValidityStatistics() {
  return useQuery({
    queryKey: ['validity-statistics'],
    queryFn: async () => {
      const response = await apiClient.get<ValidityStatistics>(
        '/api/v1/detections/validity-stats'
      )
      return response.data
    },
    refetchInterval: 300000, // Refetch every 5 minutes
  })
}
```

## Integración en Dashboard

```tsx
// Ejemplo de uso en DashboardPage.tsx

import { useValidityStatistics } from '@/hooks/useValidityStatistics'
import { Card } from '@/components/ui/Card'

export function DashboardPage() {
  const { data: stats } = useValidityStatistics()

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <Card>
        <Card.Title>Total Detecciones</Card.Title>
        <Card.Content>
          <p className="text-3xl font-bold">{stats?.total_detections || 0}</p>
        </Card.Content>
      </Card>

      <Card>
        <Card.Title>Activas</Card.Title>
        <Card.Content>
          <p className="text-3xl font-bold text-green-600">
            {stats?.active_detections || 0}
          </p>
        </Card.Content>
      </Card>

      <Card>
        <Card.Title>Por Expirar</Card.Title>
        <Card.Content>
          <p className="text-3xl font-bold text-yellow-600">
            {stats?.expiring_soon_detections || 0}
          </p>
        </Card.Content>
      </Card>

      <Card>
        <Card.Title>Expiradas</Card.Title>
        <Card.Content>
          <p className="text-3xl font-bold text-red-600">
            {stats?.expired_detections || 0}
          </p>
        </Card.Content>
      </Card>
    </div>
  )
}
```

## Permisos y Roles

Según los endpoints del backend:

- **GET /detections/expired**: Requiere autenticación (USER, EXPERT, ADMIN)
- **GET /detections/expiring-soon**: Requiere autenticación (USER, EXPERT, ADMIN)
- **POST /detections/extend-validity**: Requiere rol EXPERT o ADMIN
- **POST /detections/{id}/revalidate**: Requiere rol EXPERT o ADMIN
- **GET /detections/validity-stats**: Requiere autenticación (USER, EXPERT, ADMIN)
- **GET /detections/{id}/validity**: Requiere autenticación (USER, EXPERT, ADMIN)

## Notas de Implementación

1. **Actualización Automática**: Los componentes deberían usar React Query con `refetchInterval` para actualizar automáticamente el estado de validez.

2. **Notificaciones**: Considerar agregar notificaciones cuando:
   - Una detección está por expirar (1 día antes)
   - Una detección ha expirado
   - Se necesita revalidación

3. **Filtros en Listas**: Agregar filtros para:
   - Mostrar solo detecciones activas
   - Mostrar solo detecciones expiradas
   - Filtrar por tipo de persistencia

4. **Visualización en Mapas**: En el mapa de calor, considerar:
   - Mostrar detecciones expiradas con opacidad reducida
   - Usar color diferente para detecciones por expirar
   - Tooltip mostrando días restantes de validez

5. **Acciones Masivas**: Para expertos/admins:
   - Revalidar múltiples detecciones a la vez
   - Extender validez de detecciones por lote
