# Stack Tecnológico - Frontend Sentrix

Documentación completa de todas las herramientas, frameworks y librerías utilizadas en el frontend del proyecto Sentrix.

---

## Descripción

Frontend moderno construido con React 18 y TypeScript, que proporciona una interfaz completa para carga de imágenes, análisis con IA, visualización geoespacial y gestión de datos del sistema Sentrix.

---

## Core Framework

### React y Build Tools
- **React** `18.2.0` - Librería UI con características concurrentes
- **React DOM** `18.2.0` - Renderizado para la web
- **TypeScript** `5.9.3` - Tipado estático y mejor experiencia de desarrollo
- **Vite** `4.5.14` - Build tool ultrarrápido con HMR
- **@vitejs/plugin-react** `4.7.0` - Plugin de Vite para React

---

## Routing y Navegación

### React Router
- **react-router-dom** `6.16.0` - Routing del lado del cliente
  - Navegación declarativa
  - Lazy loading de rutas
  - Nested routing
  - Protected routes

---

## Estado y Data Fetching

### State Management
- **Zustand** `4.4.3` - Gestión de estado global ligera
  - Store simple y sin boilerplate
  - Middleware de persistencia
  - DevTools integrado
  - TypeScript first

### Server State
- **TanStack Query** `5.89.0` - Gestión de estado del servidor y caché
  - Cache inteligente
  - Automatic refetching
  - Optimistic updates
  - Mutations
  - Infinite queries
- **@tanstack/react-query-devtools** `5.89.0` - DevTools para debugging

---

## Componentes UI

### Radix UI - Componentes Headless
Sistema completo de componentes accesibles y no estilizados:

- **@radix-ui/react-alert-dialog** `1.1.15` - Diálogos de alerta
- **@radix-ui/react-avatar** `1.1.10` - Avatares de usuario
- **@radix-ui/react-checkbox** `1.3.3` - Checkboxes
- **@radix-ui/react-dialog** `1.1.15` - Modales y diálogos
- **@radix-ui/react-dropdown-menu** `2.1.16` - Menús desplegables
- **@radix-ui/react-hover-card** `1.1.15` - Cards con hover
- **@radix-ui/react-label** `2.1.7` - Labels de formularios
- **@radix-ui/react-popover** `1.1.15` - Popovers
- **@radix-ui/react-progress** `1.1.7` - Barras de progreso
- **@radix-ui/react-radio-group** `1.3.8` - Radio buttons
- **@radix-ui/react-scroll-area** `1.2.10` - Áreas de scroll personalizadas
- **@radix-ui/react-select** `2.2.6` - Selectores
- **@radix-ui/react-separator** `1.1.7` - Separadores
- **@radix-ui/react-slider** `1.3.6` - Sliders
- **@radix-ui/react-slot** `1.2.3` - Composición de componentes
- **@radix-ui/react-switch** `1.2.6` - Switches/toggles
- **@radix-ui/react-tabs** `1.1.13` - Tabs
- **@radix-ui/react-tooltip** `1.2.8` - Tooltips

### Iconos
- **lucide-react** `0.284.0` - Biblioteca de iconos moderna
  - 1000+ iconos
  - Totalmente personalizables
  - Tree-shakeable
  - TypeScript support

---

## Estilos

### Tailwind CSS Ecosystem
- **tailwindcss** `3.3.3` - Framework CSS utility-first
- **@tailwindcss/forms** `0.5.6` - Estilos para formularios
- **@tailwindcss/typography** `0.5.10` - Estilos tipográficos
- **tailwindcss-animate** `1.0.7` - Animaciones pre-construidas
- **tailwind-merge** `1.14.0` - Merge de clases de Tailwind
- **autoprefixer** `10.4.15` - Autoprefixing CSS
- **postcss** `8.4.29` - Transformación CSS

### Utilidades de Styling
- **class-variance-authority** `0.7.1` - Variantes de componentes tipadas
- **clsx** `2.1.1` - Construcción de classNames condicionales

---

## Animaciones

### Framer Motion
- **framer-motion** `11.15.0` - Librería de animaciones production-ready
  - Animaciones declarativas
  - Gestures y drag
  - Layout animations
  - Scroll animations
  - Shared layout transitions
  - SVG animations

---

## Mapas y Geolocalización

### Leaflet
- **leaflet** `1.9.4` - Librería de mapas interactivos
- **react-leaflet** `4.2.1` - Componentes React para Leaflet
- **leaflet.heat** `0.2.0` - Plugin de heatmap para Leaflet
- **@types/leaflet** `1.9.20` - Tipos TypeScript para Leaflet

**Funcionalidades:**
- Mapas interactivos
- Heatmaps de riesgo
- Markers personalizados
- Clustering de puntos
- Geolocalización
- Layers múltiples

---

## Gráficos y Visualización

### Recharts
- **recharts** `2.8.0` - Librería de gráficos composable
  - Line charts
  - Bar charts
  - Pie charts
  - Area charts
  - Radar charts
  - Composed charts
  - Responsive

---

## HTTP Client

### Axios
- **axios** `1.5.0` - Cliente HTTP basado en promesas
  - Interceptores de request/response
  - Cancelación de requests
  - Progress tracking
  - Automatic JSON transformation
  - CSRF protection

---

## Procesamiento de Imágenes

### Metadata y Conversión
- **exifr** `7.1.3` - Extracción de metadata EXIF
  - GPS coordinates
  - Camera info
  - Timestamp
  - Orientation
- **heic2any** `0.0.4` - Conversión de HEIC a JPEG/PNG
  - Soporte para imágenes de iPhone
  - Conversión en el navegador
  - Preservación de calidad

---

## UI/UX Utilities

### Notificaciones y Feedback
- **sonner** `1.7.4` - Toast notifications modernas
  - Customizable
  - Stacking automático
  - Promise-based
  - Rich content support

### Formularios y Fechas
- **react-day-picker** `9.11.1` - Date picker accesible
  - Localización
  - Rangos de fechas
  - Múltiples selecciones
  - Customizable

---

## Testing

### Testing Framework
- **vitest** `0.34.6` - Framework de testing ultrarrápido
  - Compatible con Vite
  - ESM first
  - TypeScript support
  - Watch mode inteligente
- **@vitest/ui** `0.34.4` - UI de testing interactiva

### Testing Library
- **@testing-library/react** `14.1.2` - Testing de componentes React
- **@testing-library/user-event** `14.5.1` - Simulación de eventos de usuario
- **@testing-library/jest-dom** `6.1.4` - Matchers personalizados
- **jsdom** `23.0.1` - Implementación de DOM para Node.js

---

## Linting y Formateo

### ESLint
- **eslint** `8.45.0` - Linter de JavaScript/TypeScript
- **@typescript-eslint/eslint-plugin** `6.0.0` - Reglas para TypeScript
- **@typescript-eslint/parser** `6.0.0` - Parser de TypeScript
- **eslint-plugin-react-hooks** `4.6.0` - Reglas para React Hooks
- **eslint-plugin-react-refresh** `0.4.3` - Reglas para Fast Refresh
- **eslint-plugin-jsx-a11y** `6.7.1` - Reglas de accesibilidad

### Prettier
- **prettier** `3.0.3` - Formateador de código
  - Integración con ESLint
  - Configuración consistente
  - Soporte multi-lenguaje

---

## Build y Optimización

### Vite Plugins
- **rollup-plugin-visualizer** `6.0.5` - Visualización del bundle
  - Análisis de tamaño
  - Identificación de dependencias grandes
  - Optimización del bundle

---

## TypeScript Support

### Type Definitions
- **@types/react** `18.2.15` - Tipos para React
- **@types/react-dom** `18.3.7` - Tipos para React DOM
- **@types/node** `24.6.2` - Tipos para Node.js
- **@types/leaflet** `1.9.20` - Tipos para Leaflet

---

## Arquitectura del Frontend

### Estructura de Carpetas

```
src/
├── api/                # Cliente API y configuración Axios
├── components/         # Componentes React
│   ├── ui/            # Componentes UI base (Radix + custom)
│   ├── domain/        # Componentes de dominio
│   ├── layouts/       # Layouts de página
│   ├── map/           # Componentes de mapa
│   └── public/        # Componentes públicos
├── hooks/             # Custom React hooks
├── pages/             # Páginas de la aplicación
│   ├── public/        # Páginas sin autenticación
│   └── app/           # Páginas protegidas
├── services/          # Servicios de API
├── store/             # Zustand stores
├── types/             # Tipos TypeScript compartidos
├── lib/               # Configuración y utilidades
├── utils/             # Funciones de utilidad
└── test/              # Utilidades de testing
```

---

## Patrones y Técnicas

### Component Patterns
- **Compound Components** - Componentes composables
- **Render Props** - Flexibilidad en renderizado
- **Custom Hooks** - Lógica reutilizable
- **HOCs** - Higher-Order Components cuando necesario
- **Context API** - Estado compartido localizado

### Data Fetching Patterns
- **Optimistic Updates** - UI responsive
- **Infinite Scrolling** - Carga progresiva
- **Prefetching** - Anticipación de datos
- **Stale-While-Revalidate** - Datos frescos
- **Error Boundaries** - Manejo de errores robusto

### Performance Optimizations
- **Code Splitting** - Lazy loading de rutas
- **Memoization** - React.memo, useMemo, useCallback
- **Virtual Lists** - Listas grandes optimizadas
- **Image Optimization** - Lazy loading, responsive images
- **Bundle Optimization** - Tree shaking, minification

---

## Características de Accesibilidad

### ARIA y Semántica
- Componentes Radix UI con ARIA completo
- Navegación por teclado
- Screen reader support
- Focus management
- Skip navigation links

### Testing de Accesibilidad
- eslint-plugin-jsx-a11y - Linting de accesibilidad
- Semantic HTML
- Color contrast checking

---

## Internacionalización (i18n)

### Preparado para i18n
- date-fns para formateo de fechas
- Estructura preparada para múltiples idiomas
- Formato de números localizados

---

## Progressive Web App (PWA)

### Características PWA
- Service Worker ready
- Manifest.json
- Offline capabilities (preparado)
- App icons múltiples tamaños
- Installable

---

## Seguridad

### Implementaciones de Seguridad
- JWT token storage seguro
- CSRF protection
- XSS prevention (React automatic escaping)
- Content Security Policy ready
- Sanitización de inputs
- Validación en cliente y servidor

---

## Development Experience

### Hot Module Replacement (HMR)
- Fast Refresh de React
- Instant feedback
- State preservation

### DevTools
- React DevTools support
- TanStack Query DevTools
- Zustand DevTools
- Vite DevTools

### Type Safety
- Strict TypeScript configuration
- Type checking en build
- Runtime type validation (donde necesario)

---

## Build Outputs

### Optimizaciones de Build
- Minificación de JS/CSS
- Tree shaking
- Code splitting automático
- Asset optimization
- Gzip/Brotli compression ready

### Tamaños de Bundle (aproximados)
- Chunk principal: ~150KB (gzipped)
- Vendor chunk: ~200KB (gzipped)
- Total inicial: ~350KB (gzipped)

---

## Deployment

### Plataformas Soportadas
- Vercel (configurado)
- Netlify
- Nginx (con nginx-cache.conf)
- Docker
- Hostinger + Dokploy

### Variables de Entorno
```bash
VITE_API_URL              # URL del backend
VITE_API_BASE_URL         # Base path de la API
VITE_SUPABASE_URL         # Supabase project URL
VITE_SUPABASE_ANON_KEY    # Supabase anon key
VITE_ENV                  # Entorno (development/production)
```

---

## Navegadores Soportados

### Compatibilidad
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Opera 76+
- Mobile browsers (iOS Safari, Chrome Android)

---

## Métricas de Rendimiento

### Core Web Vitals Targets
- **LCP** (Largest Contentful Paint): < 2.5s
- **FID** (First Input Delay): < 100ms
- **CLS** (Cumulative Layout Shift): < 0.1
- **FCP** (First Contentful Paint): < 1.8s
- **TTI** (Time to Interactive): < 3.8s

---

**Versión:** 1.0.0
**Framework:** React 18 + Vite + TypeScript
**Total de Dependencias:** 60+ (20 dev, 40+ prod)
**Última actualización:** Noviembre 2025
