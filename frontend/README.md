# Frontend - Sentrix

Aplicación web moderna basada en React para la plataforma Sentrix, que proporciona una interfaz intuitiva para detección y análisis de criaderos de dengue.

## Descripción General

El frontend de Sentrix es una Single Page Application (SPA) construida con React 18 y TypeScript, que ofrece una interfaz completa para carga de imágenes, análisis con IA, visualización geoespacial y gestión de datos.

### Funcionalidades Principales

- **Carga y Análisis de Imágenes** - Interfaz drag-and-drop para carga individual y masiva
- **Dashboard Interactivo** - Estadísticas en tiempo real, gráficos y visualización de riesgo
- **Mapas Geoespaciales** - Heatmaps basados en Leaflet mostrando ubicaciones de detecciones
- **Visualización Dual de Imágenes** - Comparación lado a lado de imágenes originales y procesadas
- **Validación de Expertos** - Interfaz para revisar y validar detecciones de IA
- **Gestión de Usuarios** - Panel de administración para usuarios y roles
- **Generación de Reportes** - Exportación de datos en PDF, CSV o JSON
- **Diseño Responsive** - Enfoque mobile-first con Tailwind CSS
- **UI Basada en Roles** - Interfaz dinámica según permisos de usuario (USER, EXPERT, ADMIN)

## Arquitectura

### Stack Tecnológico

| Componente | Tecnología | Propósito |
|-----------|-----------|-----------|
| **Framework** | React 18.2 | Librería UI con características concurrentes |
| **Lenguaje** | TypeScript 5.9 | Tipado estático y mejor experiencia de desarrollo |
| **Build Tool** | Vite 4.5 | Desarrollo y builds ultrarrápidos |
| **Estado Global** | Zustand 4.4 | Gestión de estado ligera |
| **Data Fetching** | TanStack Query 5 | Gestión de estado del servidor y caché |
| **Routing** | React Router 6 | Routing del lado del cliente con lazy loading |
| **Estilos** | Tailwind CSS 3.3 | Framework CSS utility-first |
| **Mapas** | React Leaflet 4.2 | Visualización geoespacial interactiva |
| **Gráficos** | Recharts 2.8 | Componentes de visualización de datos |
| **Testing** | Vitest + React Testing Library | Framework de testing moderno |
| **Componentes UI** | Radix UI | Componentes headless accesibles |

### Estructura del Proyecto

```
frontend/
├── public/                         # Assets estáticos
│   ├── fonts/                     # Fuentes personalizadas
│   ├── images/                    # Imágenes e íconos
│   └── Icon-Sentrix-*.png        # Íconos de app
│
├── src/
│   ├── main.tsx                   # Punto de entrada
│   ├── App.tsx                    # Componente raíz con routing
│   ├── globals.css                # Estilos globales
│   │
│   ├── api/                       # Capa de cliente API
│   │   └── client.ts             # Instancia axios configurada
│   │
│   ├── components/
│   │   ├── ui/                   # Componentes UI reutilizables
│   │   ├── domain/               # Componentes específicos del dominio
│   │   ├── map/                  # Componentes de mapa
│   │   └── layouts/              # Layouts de página
│   │
│   ├── pages/
│   │   ├── public/               # Páginas públicas (sin auth)
│   │   └── app/                  # Páginas protegidas (con auth)
│   │
│   ├── hooks/                    # Custom React hooks
│   ├── services/                 # Capa de servicios API
│   ├── store/                    # Stores de Zustand
│   ├── types/                    # Tipos TypeScript
│   ├── lib/                      # Configuración y utilidades
│   └── test/                     # Utilidades de testing
│
├── package.json
├── vite.config.ts
├── vitest.config.ts
├── tailwind.config.js
└── vercel.json
```

## Instalación

### Requisitos Previos

- Node.js 18+ (se recomienda versión LTS)
- npm 9+ o yarn 1.22+
- API backend ejecutándose (por defecto: http://localhost:8000)

### Pasos de Configuración

1. **Navegar al directorio frontend**
   ```bash
   cd frontend
   ```

2. **Instalar dependencias**
   ```bash
   npm install
   ```

3. **Configurar variables de entorno**

   Crear archivo `.env` en el directorio `frontend/`:

   ```bash
   # Configuración de API
   VITE_API_URL=http://localhost:8000
   VITE_API_BASE_URL=http://localhost:8000/api

   # Supabase (para acceso directo a storage)
   VITE_SUPABASE_URL=https://tu-proyecto.supabase.co
   VITE_SUPABASE_ANON_KEY=tu-anon-key

   # Opcional: Nombre del entorno
   VITE_ENV=development
   ```

4. **Iniciar servidor de desarrollo**
   ```bash
   npm run dev
   ```

5. **Acceder a la aplicación**
   - Desarrollo: http://localhost:5173
   - El puerto puede variar; verificar salida de consola

## Configuración

### Variables de Entorno

Todas las variables de entorno deben tener el prefijo `VITE_` para estar expuestas al cliente.

| Variable | Requerida | Por Defecto | Descripción |
|----------|-----------|-------------|-------------|
| `VITE_API_URL` | Sí | - | URL base de la API backend |
| `VITE_API_BASE_URL` | Sí | - | Ruta base de API v1 |
| `VITE_SUPABASE_URL` | Opcional | - | URL del proyecto Supabase |
| `VITE_SUPABASE_ANON_KEY` | Opcional | - | Anon key de Supabase |
| `VITE_ENV` | No | `development` | Nombre del entorno |

## Scripts Disponibles

```bash
# Desarrollo
npm run dev              # Iniciar servidor dev con HMR
npm run build            # Build de producción
npm run preview          # Preview del build de producción

# Calidad de Código
npm run lint             # Ejecutar ESLint
npm run lint:fix         # Corregir problemas de ESLint
npm run typecheck        # Type checking de TypeScript
npm run format           # Formatear código con Prettier

# Testing
npm run test             # Ejecutar tests en modo watch
npm run test:ui          # Abrir UI de Vitest
npm run test:coverage    # Generar reporte de cobertura
```

## Ejemplos de Uso

### Autenticación

```typescript
import { useAuthStore } from '@/store/auth'

function LoginComponent() {
  const { login, isLoading } = useAuthStore()

  const handleLogin = async (email: string, password: string) => {
    try {
      await login({ email, password })
      // Redirección automática al dashboard
    } catch (error) {
      console.error('Error en login:', error)
    }
  }

  return (
    // JSX del formulario de login
  )
}
```

### Llamadas a API con React Query

```typescript
import { useQuery, useMutation } from '@tanstack/react-query'
import { apiClient } from '@/api/client'

// Obtener datos
function AnalysisList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['analyses'],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/analyses')
      return response.data
    },
  })

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage error={error} />

  return <AnalysisTable data={data} />
}

// Mutar datos
function UploadForm() {
  const mutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      return apiClient.post('/api/v1/analyses', formData)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['analyses'] })
    },
  })

  return (
    <button onClick={() => mutation.mutate(file)}>
      Subir
    </button>
  )
}
```

### Gestión de Estado con Zustand

```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  user: User | null
  token: string | null
  setUser: (user: User) => void
  setTokens: (token: string, refreshToken: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      setUser: (user) => set({ user }),
      setTokens: (token, refreshToken) => set({ token, refreshToken }),
      logout: () => set({ user: null, token: null, refreshToken: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        refreshToken: state.refreshToken,
      }),
    }
  )
)
```

## Funcionalidades Clave

### 1. Flujo de Autenticación

La aplicación usa autenticación basada en JWT con refresh automático de tokens:

```
1. Usuario inicia sesión → Recibe access_token y refresh_token
2. Tokens almacenados en Zustand (persistidos en localStorage)
3. Cliente API agrega automáticamente header Authorization
4. En respuesta 401 → Intenta refresh de token
5. Si refresh falla → Redirección a login
```

### 2. Renderizado Basado en Roles

Diferentes elementos de UI según el rol del usuario:

```typescript
const { user } = useAuthStore()
const isAdmin = user?.role === 'ADMIN'
const isExpert = user?.role === 'EXPERT' || isAdmin

return (
  <>
    {/* Todos los usuarios ven esto */}
    <AnalysisList />

    {/* Solo expertos y admins ven esto */}
    {isExpert && <ValidationQueue />}

    {/* Solo admins ven esto */}
    {isAdmin && <UserManagement />}
  </>
)
```

### 3. Carga de Imágenes con Progreso

```typescript
import { useState } from 'react'
import { DropZone } from '@/components/domain/DropZone'
import { ProgressBar } from '@/components/ui/ProgressBar'

function UploadPage() {
  const [progress, setProgress] = useState(0)

  const handleUpload = async (files: File[]) => {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))

    const response = await apiClient.post('/api/v1/analyses', formData, {
      onUploadProgress: (progressEvent) => {
        const percent = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        )
        setProgress(percent)
      },
    })

    return response.data
  }

  return (
    <div>
      <DropZone onDrop={handleUpload} multiple maxSize={10 * 1024 * 1024} />
      {progress > 0 && <ProgressBar value={progress} />}
    </div>
  )
}
```

### 4. Visualización Geoespacial

```typescript
import { HeatMap } from '@/components/map/HeatMap'

function MapView({ detections }: { detections: Detection[] }) {
  const points = detections
    .filter(d => d.latitude && d.longitude)
    .map(d => ({
      lat: d.latitude,
      lng: d.longitude,
      intensity: d.risk_score,
    }))

  return (
    <HeatMap
      center={[-34.603722, -58.381592]}
      zoom={12}
      points={points}
    />
  )
}
```

## Testing

### Ejecutar Tests

```bash
# Ejecutar todos los tests
npm run test

# Modo watch
npm run test -- --watch

# Modo UI
npm run test:ui

# Cobertura
npm run test:coverage
```

### Escribir Tests

Ejemplo de test de componente:

```typescript
import { describe, it, expect } from 'vitest'
import { render, screen, userEvent } from '@/test/utils'
import { Button } from './Button'

describe('Button', () => {
  it('renderiza con texto', () => {
    render(<Button>Hacer clic</Button>)
    expect(screen.getByRole('button', { name: /hacer clic/i }))
      .toBeInTheDocument()
  })

  it('maneja eventos de clic', async () => {
    const handleClick = vi.fn()
    const user = userEvent.setup()

    render(<Button onClick={handleClick}>Clic</Button>)
    await user.click(screen.getByRole('button'))

    expect(handleClick).toHaveBeenCalledOnce()
  })

  it('puede estar deshabilitado', () => {
    render(<Button disabled>Clic</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })
})
```

## Deployment

### Build para Producción

```bash
# Crear build optimizado de producción
npm run build

# Directorio de salida: dist/
```

### Deployment en Vercel (Recomendado)

1. **Conectar repositorio a Vercel**
   - Importar proyecto en dashboard de Vercel
   - Seleccionar `frontend` como directorio raíz
   - Framework: Vite
   - Build command: `npm run build`
   - Output directory: `dist`

2. **Configurar variables de entorno en Vercel:**
   ```
   VITE_API_URL=https://tu-backend.com
   VITE_API_BASE_URL=https://tu-backend.com/api
   VITE_SUPABASE_URL=https://tu-proyecto.supabase.co
   VITE_SUPABASE_ANON_KEY=tu-anon-key
   ```

3. **Deploy:**
   - Push a rama `main` → Deploy automático a producción
   - Push a feature branch → Deploy de preview con URL única

### Otras Plataformas

**Netlify:**
```bash
# Build command
npm run build

# Publish directory
dist

# Reglas de redirección (netlify.toml)
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

**Docker:**
```dockerfile
# Build multi-stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Optimización de Rendimiento

### Code Splitting

Lazy load de rutas para bundle inicial más pequeño:

```typescript
import { lazy, Suspense } from 'react'

const DashboardPage = lazy(() => import('@/pages/app/DashboardPage'))
const AnalysisPage = lazy(() => import('@/pages/app/AnalysisPage'))

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/app/dashboard" element={<DashboardPage />} />
        <Route path="/app/analyses" element={<AnalysisPage />} />
      </Routes>
    </Suspense>
  )
}
```

### Caché de React Query

Configurar caché inteligente:

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,      // 5 minutos
      cacheTime: 10 * 60 * 1000,     // 10 minutos
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
    },
  },
})
```

## Solución de Problemas

### Problemas Comunes

**Problema:** `Module not found: Error: Can't resolve '@/...'`

**Solución:** Verificar que `tsconfig.json` tenga el mapeo de paths correcto:
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

**Problema:** Errores de CORS al llamar a la API

**Solución:**
1. Verificar que la configuración CORS del backend permita el origen del frontend
2. Usar proxy de Vite en desarrollo:
```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
```

**Problema:** Variables de entorno no funcionan

**Solución:**
1. Asegurar que las variables tengan prefijo `VITE_`
2. Reiniciar servidor dev después de cambiar `.env`
3. Verificar import: `import.meta.env.VITE_API_URL`

**Problema:** Errores de build relacionados con TypeScript

**Solución:**
```bash
# Limpiar caché y reinstalar
rm -rf node_modules package-lock.json
npm install

# Ejecutar type checking
npm run typecheck
```

## Licencia

Este proyecto está licenciado bajo la Licencia MIT.

---

**Versión:** 2.5.0
**Framework:** React 18 + Vite + TypeScript
**Estado:** Listo para Producción
**Última Actualización:** Octubre 2024
