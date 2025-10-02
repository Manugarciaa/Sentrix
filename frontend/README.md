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
│   ├── api/              # Clientes de API
│   ├── components/       # Componentes reutilizables
│   │   ├── ui/          # Componentes básicos (shadcn)
│   │   └── layouts/     # Layouts de página
│   ├── pages/           # Páginas principales
│   ├── store/           # Estado global (Zustand)
│   ├── hooks/           # Hooks personalizados
│   ├── utils/           # Utilidades
│   ├── types/           # TypeScript types
│   ├── lib/             # Config y constantes
│   └── mocks/           # MSW mocks (dev)
├── public/              # Assets estáticos
├── dist/                # Build producción
├── vercel.json          # Config Vercel
├── vite.config.ts       # Config Vite
└── tailwind.config.js   # Config Tailwind
```

## 🛠️ Instalación y Desarrollo

### Variables de Entorno

Copia `.env.example` a `.env`:

```bash
# Development
VITE_API_URL=http://localhost:8000
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_YOLO_SERVICE_URL=http://localhost:8001

# Production (configurar en Vercel)
# VITE_API_URL=https://sentrix-backend.onrender.com
# VITE_API_BASE_URL=https://sentrix-backend.onrender.com/api/v1
# VITE_YOLO_SERVICE_URL=https://sentrix-yolo.onrender.com
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

### Vercel (Recomendado)

1. **Conectar repositorio en Vercel**
   - Framework Preset: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`

2. **Variables de entorno en Vercel**:
   ```bash
   VITE_API_URL=https://sentrix-backend.onrender.com
   VITE_API_BASE_URL=https://sentrix-backend.onrender.com/api/v1
   VITE_YOLO_SERVICE_URL=https://sentrix-yolo.onrender.com
   VITE_ENV=production
   ```

3. **Deploy automático**
   - Push a `main` → Deploy automático
   - Pull Request → Preview deployment

### Build Local

```bash
# Generar build optimizado
npm run build

# Preview local
npm run preview
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

- [Backend API](../backend/README.md)
- [YOLO Service](../yolo-service/README.md)
- [Librería Compartida](../shared/README.md)

---

**Puerto**: 3000 | **Framework**: React 18 + Vite + TypeScript | **Deploy**: Vercel