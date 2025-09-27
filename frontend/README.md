# Sentrix Frontend - Interfaz Web

Aplicación web desarrollada en React/TypeScript para la plataforma Sentrix de detección de criaderos de *Aedes aegypti*. Proporciona una interfaz completa para análisis de imágenes, visualización de resultados y gestión de datos.

## Descripción

El frontend de Sentrix es una Single Page Application (SPA) que permite:

- **Análisis de imágenes** - Carga y procesamiento con IA
- **Dashboard interactivo** - Visualización de estadísticas y métricas
- **Gestión de detecciones** - Revisión y validación de resultados
- **Mapa geoespacial** - Visualización de ubicaciones de riesgo
- **Sistema de usuarios** - Autenticación y roles diferenciados
- **Exportación de datos** - Reportes en múltiples formatos
- **Visualización dual** - Imágenes originales y procesadas con marcadores
- **Métricas de optimización** - Estadísticas de deduplicación y ahorro de storage

## Arquitectura Tecnológica

### Stack Principal
- **React 18** - Framework de interfaz de usuario
- **TypeScript** - Tipado estático y desarrollo moderno
- **Vite** - Build tool y desarrollo rápido
- **Zustand** - Gestión de estado global
- **Axios** - Cliente HTTP para APIs
- **React Router** - Navegación SPA

### Bibliotecas UI
- **Tailwind CSS** - Framework de estilos utility-first
- **Headless UI** - Componentes accesibles
- **React Leaflet** - Mapas interactivos
- **Recharts** - Gráficos y visualizaciones
- **React Hook Form** - Manejo de formularios

## Estructura del Proyecto

```
frontend/
├── src/
│   ├── api/                # Clientes de API
│   │   ├── client.ts      # Cliente base con interceptors
│   │   ├── auth.ts        # API de autenticación
│   │   ├── analyses.ts    # API de análisis
│   │   ├── reports.ts     # API de reportes
│   │   └── yolo.ts        # API del servicio YOLO
│   ├── components/        # Componentes reutilizables
│   │   ├── ui/           # Componentes básicos de UI
│   │   └── layouts/      # Layouts de página
│   ├── pages/            # Páginas de la aplicación
│   ├── store/            # Estado global (Zustand)
│   ├── hooks/            # Hooks personalizados
│   ├── utils/            # Utilidades y helpers
│   ├── types/            # Definiciones TypeScript
│   └── lib/              # Configuración y constantes
├── public/               # Archivos estáticos
└── dist/                 # Build de producción
```

## 🛠️ Instalación y Desarrollo

### Variables de Entorno

```bash
# APIs y servicios
VITE_API_BASE_URL=http://localhost:8000
VITE_YOLO_SERVICE_URL=http://localhost:8001

# Características opcionales
VITE_ENABLE_MOCKING=false
VITE_LOG_LEVEL=info

# Base de datos (opcional para desarrollo)
VITE_SUPABASE_URL=tu_url_supabase
VITE_SUPABASE_ANON_KEY=tu_clave_anonima
```

### Instalación y Desarrollo

```bash
# Instalar dependencias
npm install

# Desarrollo local (puerto 3000)
npm run dev

# Build para producción
npm run build

# Preview de producción
npm run preview

# Linting y formato
npm run lint
npm run lint:fix
```


## APIs Integradas

### Backend API (Puerto 8000)
- **Autenticación** - Login, registro, tokens
- **Análisis** - CRUD y filtros avanzados con almacenamiento dual
- **Detecciones** - Validación y gestión
- **Reportes** - Estadísticas, métricas y deduplicación
- **Sistema** - Health checks e información
- **Storage** - Gestión inteligente de imágenes con nomenclatura estandarizada

### YOLO Service (Puerto 8001)
- **Detección** - Procesamiento directo de imágenes
- **Modelos** - Información de modelos disponibles
- **Health** - Estado del servicio de IA
- **Imágenes procesadas** - Generación automática con marcadores azules

### Cliente API Unificado

```typescript
import { api } from '@/api/client'
import { yoloApi } from '@/api/yolo'

// API del backend con almacenamiento dual
const analyses = await api.get('/api/v1/analyses')

// Servicio YOLO directo
const result = await yoloApi.detect(imageFile, {
  confidence_threshold: 0.7,
  include_gps: true
})

// Métricas de deduplicación
const deduplicationStats = await api.get('/api/v1/reports/deduplication')
```

## Nuevas Funcionalidades de Visualización

### Visualización Dual de Imágenes
El frontend ahora muestra tanto la imagen original como la procesada con marcadores:

```typescript
interface AnalysisResult {
  image_urls: {
    original: string     // Imagen sin modificaciones
    processed: string    // Con marcadores azules de detecciones
  }
  filenames: {
    original: string
    standardized: string
    processed: string
  }
}
```

### Componente de Imágenes Duales
```typescript
import { DualImageViewer } from '@/components/DualImageViewer'

<DualImageViewer
  originalUrl={analysis.image_urls.original}
  processedUrl={analysis.image_urls.processed}
  detections={analysis.detections}
  showToggle={true}
/>
```

### Dashboard de Optimización
Nuevas métricas de deduplicación y ahorro de storage:

```typescript
interface DeduplicationMetrics {
  total_analyses: number
  unique_images: number
  duplicate_references: number
  deduplication_rate: number
  storage_saved_mb: number
  storage_saved_gb: number
}
```

## Gestión de Estado

### Stores Principales

```typescript
// Estado de autenticación
import { useAuthStore } from '@/store/auth'
const { user, login, logout } = useAuthStore()

// Estado de análisis
import { useAnalysisStore } from '@/store/analysis'
const { analyses, filters, loadAnalyses } = useAnalysisStore()

// Estado de aplicación
import { useAppStore } from '@/store/app'
const { theme, notifications, addNotification } = useAppStore()
```

## Formatos de Imagen Soportados

- **JPEG/JPG** - Formato estándar
- **PNG** - Con soporte de transparencia
- **HEIC/HEIF** - Formato Apple (conversión automática)
- **TIFF** - Alta calidad
- **WebP** - Formato web moderno
- **BMP** - Bitmap básico

### Restricciones
- **Tamaño máximo**: 50MB
- **Validación automática** - Formato y tamaño
- **Metadatos GPS** - Extracción automática cuando disponible

## Sistema de Roles

```typescript
export enum UserRole {
  ADMIN = 'ADMIN',     // Administrador completo
  EXPERT = 'EXPERT',   // Experto en validación
  USER = 'USER'        // Usuario estándar
}
```

### Permisos por Rol
- **USER**: Subir imágenes, ver sus análisis
- **EXPERT**: Validar detecciones, acceso a reportes
- **ADMIN**: Gestión de usuarios, configuración del sistema

## Navegación y Rutas

### Rutas Públicas
- `/` - Página de inicio
- `/about` - Información del proyecto
- `/prevention` - Guías de prevención
- `/map` - Mapa público de riesgo
- `/login` - Inicio de sesión
- `/register` - Registro de usuario

### Rutas Privadas (Dashboard)
- `/app/dashboard` - Panel principal
- `/app/analysis` - Lista de análisis
- `/app/analysis/:id` - Detalle de análisis
- `/app/uploads` - Subida de imágenes
- `/app/reports` - Reportes y estadísticas
- `/app/settings` - Configuración

## Componentes Principales

### Upload de Imágenes
```typescript
import { ImageUpload } from '@/components/ImageUpload'

<ImageUpload
  onUpload={(files) => handleUpload(files)}
  maxSize={50 * 1024 * 1024}
  accept="image/*"
  multiple
/>
```

### Mapa de Detecciones
```typescript
import { DetectionMap } from '@/components/DetectionMap'

<DetectionMap
  markers={detectionMarkers}
  center={[-12.0464, -77.0428]}
  zoom={13}
  onMarkerClick={handleMarkerClick}
/>
```

### Dashboard de Métricas
```typescript
import { MetricsDashboard } from '@/components/MetricsDashboard'

<MetricsDashboard
  data={statisticsData}
  timeRange="7d"
  refreshInterval={30000}
/>
```

## Integración con Servicios

### Flujo de Análisis Mejorado

1. **Upload** - Usuario sube imagen
2. **Validación** - Frontend valida formato/tamaño
3. **Envío** - Imagen enviada al backend
4. **Deduplicación** - Backend verifica duplicados automáticamente
5. **Procesamiento** - Backend comunica con YOLO service
6. **Almacenamiento Dual** - Generación de imagen original y procesada
7. **Nomenclatura** - Aplicación de sistema estandarizado de nombres
8. **Resultados** - Frontend recibe URLs de ambas imágenes y metadatos
9. **Visualización Dual** - Mostrar original y procesada con toggle interactivo

### Manejo de Errores

```typescript
// Interceptor global de errores
apiClient.interceptors.response.use(
  response => response,
  error => {
    // Manejo automático de errores 401, 500, etc.
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
    }
    return Promise.reject(error)
  }
)
```

## Testing

```bash
# Tests unitarios
npm run test

# Tests de componentes
npm run test:components

# Tests de integración
npm run test:integration

# Coverage completo
npm run test:coverage
```

## Deployment

### Build para Producción

```bash
# Generar build optimizado
npm run build

# Verificar build
npm run preview

# Análisis de bundle
npm run analyze
```

### Variables de Producción

```bash
VITE_API_BASE_URL=https://api.sentrix.com
VITE_YOLO_SERVICE_URL=https://yolo.sentrix.com
VITE_LOG_LEVEL=warn
```

## Integración con Backend

### Sincronización de Enums

```typescript
// Enums sincronizados con shared library
export const riskLevels = {
  ALTO: 'ALTO',
  MEDIO: 'MEDIO',
  BAJO: 'BAJO',
  MINIMO: 'MINIMO'
} as const

export const userRoles = {
  USER: 'USER',
  ADMIN: 'ADMIN',
  EXPERT: 'EXPERT'
} as const
```

### Validación Consistente

```typescript
export const fileConstraints = {
  maxSize: 50 * 1024 * 1024, // 50MB
  allowedTypes: [
    'image/jpeg', 'image/jpg', 'image/png',
    'image/tiff', 'image/heic', 'image/heif',
    'image/webp', 'image/bmp'
  ]
}
```

## Documentación Adicional

- [Scripts de Utilidad](../scripts/README.md)
- [Librería Compartida](../shared/README.md)
- [Backend API](../backend/README.md)

---

## Actualizaciones Recientes (v1.2.0)

### Nuevas Funcionalidades Implementadas:
- **Visualización Dual de Imágenes**: Componentes para mostrar imagen original y procesada
- **Dashboard de Optimización**: Métricas de deduplicación y ahorro de storage
- **Integración Mejorada**: APIs actualizadas para almacenamiento dual
- **Interfaz Profesional**: Componentes específicos para nuevas funcionalidades

### Mejoras en UX/UI:
- **DualImageViewer**: Componente con toggle para alternar entre vistas
- **Métricas de Storage**: Visualización de estadísticas de optimización
- **Nomenclatura Estandarizada**: Interfaz que refleja el sistema profesional de archivos
- **Estados de Carga**: Indicadores para procesamiento de imágenes duales

### Integración Backend:
- **APIs Actualizadas**: Soporte para endpoints de deduplicación
- **Tipos TypeScript**: Interfaces actualizadas para almacenamiento dual
- **Gestión de Estado**: Stores mejorados para nuevas funcionalidades
- **Manejo de Errores**: Cobertura para nuevos flujos de procesamiento

### Estado Actual:
- **Frontend funcionando** en puerto 3000 con funcionalidades avanzadas
- **Conexión dual** con backend y YOLO service verificada
- **Visualización mejorada** de resultados de análisis
- **TypeScript** sin errores con nuevas interfaces
- **Diseño responsive** mantenido para todos los dispositivos

### Características Técnicas:
- **Componentes modulares**: Arquitectura escalable para nuevas funcionalidades
- **Performance optimizada**: Carga eficiente de imágenes duales
- **Estado consistente**: Sincronización con backend mejorada
- **Tipado fuerte**: TypeScript completo para nuevas APIs

### Contexto Académico Actualizado:
- **Universidad**: Nacional de Tucumán, Argentina
- **Enfoque**: Detección con IA y gestión inteligente de imágenes
- **Investigación**: YOLOv11 + sistema de deduplicación para salud pública
- **Objetivo**: Herramienta optimizada para prevención de dengue en zonas urbanas
- **Novedad**: Sistema profesional de nomenclatura y almacenamiento eficiente

---

**Versión**: 1.2.0 | **Puerto**: 3000 | **Framework**: React 18 + TypeScript | **Estado**: Funcional con gestión avanzada de imágenes