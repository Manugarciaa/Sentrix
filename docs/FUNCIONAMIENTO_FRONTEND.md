# Como Funciona Frontend

Documentacion detallada del funcionamiento interno de la aplicacion web de Sentrix.

---

# FRONTEND - Aplicacion React

## Descripcion General

El Frontend es la interfaz de usuario de Sentrix. Construido con React 18, TypeScript y Vite, proporciona una experiencia moderna y responsiva para subir imagenes, visualizar analisis y explorar mapas de calor de criaderos.

---

## Arquitectura de la Aplicacion

### Stack Principal

```
React 18.2          - Libreria UI
TypeScript 5.9      - Tipado estatico
Vite 4.5            - Build tool
TailwindCSS 3.3     - Estilos
Zustand             - State management
TanStack Query      - Data fetching y cache
React Router 6      - Routing
React Leaflet       - Mapas interactivos
```

### Estructura de Carpetas

```
frontend/src/
├── components/
│   ├── domain/          # Componentes de negocio
│   │   ├── AnalysisCard.tsx
│   │   ├── FilterBar.tsx
│   │   ├── ImageViewer.tsx
│   │   ├── HeatMap.tsx
│   │   ├── LocationPicker.tsx
│   │   └── UploadModal.tsx
│   ├── layouts/         # Layouts de paginas
│   │   ├── AppLayout.tsx
│   │   ├── AuthLayout.tsx
│   │   ├── AuthLayoutWrapper.tsx
│   │   └── PublicLayout.tsx
│   ├── map/            # Componentes de mapa
│   │   └── HeatMap.tsx
│   ├── public/         # Componentes publicos
│   │   ├── AboutDengue.tsx
│   │   ├── AboutSentrix.tsx
│   │   └── DemoSection.tsx
│   └── ui/             # Componentes UI base (Radix)
│       ├── Badge.tsx
│       ├── Button.tsx
│       ├── ErrorBoundary.tsx
│       └── custom-skeletons.tsx
│
├── pages/              # Paginas de la aplicacion
│   ├── app/           # Paginas autenticadas
│   │   ├── DashboardPage.tsx
│   │   ├── AnalysisPage.tsx
│   │   ├── AnalysisDetailPage.tsx
│   │   └── UploadsPage.tsx
│   └── public/        # Paginas publicas
│       ├── HomePage.tsx
│       ├── LoginPage.tsx
│       ├── RegisterPage.tsx
│       └── NotFoundPage.tsx
│
├── api/               # Cliente HTTP
│   └── client.ts      # Axios instance + endpoints
│
├── hooks/             # Custom hooks
│   └── useAuthMutations.ts
│
├── lib/               # Utilidades
│   └── config.ts      # Configuracion
│
├── types/             # TypeScript types
│   └── index.ts
│
├── App.tsx            # Componente raiz
├── main.tsx           # Entry point
└── globals.css        # Estilos globales
```

---

## Flujo de Autenticacion

### 1. Login de Usuario

**Componente:** `LoginPage.tsx`

**Proceso:**

```typescript
// 1. Formulario de login
const LoginPage = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // 2. Llama al backend
      const response = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data = await response.json();

      // 3. Guarda token en localStorage
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      localStorage.setItem('user', JSON.stringify(data.user));

      // 4. Redirige a dashboard
      navigate('/app/dashboard');

    } catch (error) {
      console.error('Login error:', error);
      // Muestra error al usuario
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
};
```

### 2. Proteccion de Rutas

**Router Configuration:**

```typescript
// App.tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const token = localStorage.getItem('access_token');

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Rutas publicas */}
        <Route path="/" element={<PublicLayout />}>
          <Route index element={<HomePage />} />
          <Route path="login" element={<LoginPage />} />
          <Route path="register" element={<RegisterPage />} />
        </Route>

        {/* Rutas protegidas */}
        <Route
          path="/app"
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="analyses" element={<AnalysisPage />} />
          <Route path="analyses/:id" element={<AnalysisDetailPage />} />
          <Route path="uploads" element={<UploadsPage />} />
        </Route>

        {/* 404 */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
};
```

### 3. Cliente HTTP con Interceptores

**api/client.ts:**

```typescript
import axios from 'axios';

// 1. Crea instancia de Axios
export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 2. Interceptor de request (agrega token)
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 3. Interceptor de response (maneja errores)
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Si error 401 y no es refresh, intenta refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');

        const response = await axios.post(
          `${apiClient.defaults.baseURL}/api/v1/auth/refresh`,
          { refresh_token: refreshToken }
        );

        const { access_token } = response.data;

        localStorage.setItem('access_token', access_token);

        originalRequest.headers.Authorization = `Bearer ${access_token}`;

        return apiClient(originalRequest);

      } catch (refreshError) {
        // Refresh fallo, logout
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// 4. API endpoints
export const analysisApi = {
  // Listar analisis
  getAll: (params?: { page?: number; limit?: number; risk_level?: string }) =>
    apiClient.get('/api/v1/analyses', { params }),

  // Obtener por ID
  getById: (id: string) =>
    apiClient.get(`/api/v1/analyses/${id}`),

  // Crear analisis
  create: (formData: FormData) =>
    apiClient.post('/api/v1/analyses', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),

  // Eliminar analisis
  delete: (id: string) =>
    apiClient.delete(`/api/v1/analyses/${id}`),

  // Descargar reporte PDF
  downloadReport: (id: string) =>
    apiClient.get(`/api/v1/analyses/${id}/report`, {
      responseType: 'blob'
    })
};

export const authApi = {
  login: (email: string, password: string) =>
    apiClient.post('/api/v1/auth/login', { email, password }),

  register: (email: string, password: string, name: string) =>
    apiClient.post('/api/v1/auth/register', { email, password, name }),

  logout: () =>
    apiClient.post('/api/v1/auth/logout')
};
```

---

## Flujo de Subida y Analisis de Imagen

### 1. Modal de Subida

**Componente:** `UploadModal.tsx`

```typescript
import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { analysisApi } from '@/api/client';

const UploadModal = ({ open, onClose }: UploadModalProps) => {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [latitude, setLatitude] = useState<number | null>(null);
  const [longitude, setLongitude] = useState<number | null>(null);
  const [locationSource, setLocationSource] = useState<'AUTO' | 'MANUAL'>('AUTO');

  const queryClient = useQueryClient();

  // 1. Mutation para crear analisis
  const createMutation = useMutation({
    mutationFn: (formData: FormData) => analysisApi.create(formData),
    onSuccess: () => {
      // Invalida cache de analisis para refrescar lista
      queryClient.invalidateQueries({ queryKey: ['analyses'] });
      onClose();
    },
    onError: (error) => {
      console.error('Upload failed:', error);
    }
  });

  // 2. Maneja seleccion de archivo
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];

    if (!selectedFile) return;

    // Validacion de tamano
    const MAX_SIZE = 50 * 1024 * 1024; // 50MB
    if (selectedFile.size > MAX_SIZE) {
      alert('File too large. Max size: 50MB');
      return;
    }

    // Validacion de tipo
    const ALLOWED_TYPES = [
      'image/jpeg', 'image/png', 'image/heic',
      'image/tiff', 'image/bmp', 'image/webp'
    ];

    if (!ALLOWED_TYPES.includes(selectedFile.type)) {
      alert(`Invalid file type. Allowed: ${ALLOWED_TYPES.join(', ')}`);
      return;
    }

    setFile(selectedFile);

    // 3. Genera preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result as string);
    };
    reader.readAsDataURL(selectedFile);
  };

  // 4. Obtiene ubicacion del navegador
  const getCurrentLocation = () => {
    if (!navigator.geolocation) {
      alert('Geolocation not supported');
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLatitude(position.coords.latitude);
        setLongitude(position.coords.longitude);
        setLocationSource('MANUAL');
      },
      (error) => {
        console.error('Geolocation error:', error);
        alert('Failed to get location');
      }
    );
  };

  // 5. Maneja submit
  const handleSubmit = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    if (latitude && longitude) {
      formData.append('latitude', latitude.toString());
      formData.append('longitude', longitude.toString());
      formData.append('location_source', locationSource);
    }

    createMutation.mutate(formData);
  };

  return (
    <div className="modal">
      <h2>Upload Image for Analysis</h2>

      {/* File input */}
      <input
        type="file"
        accept="image/jpeg,image/png,image/heic,image/tiff,image/bmp,image/webp"
        onChange={handleFileChange}
      />

      {/* Preview */}
      {preview && (
        <img src={preview} alt="Preview" className="w-full max-h-64 object-contain" />
      )}

      {/* Location picker */}
      <div>
        <button onClick={getCurrentLocation}>
          Get Current Location
        </button>

        {latitude && longitude && (
          <p>Location: {latitude}, {longitude}</p>
        )}
      </div>

      {/* Submit */}
      <button
        onClick={handleSubmit}
        disabled={!file || createMutation.isPending}
      >
        {createMutation.isPending ? 'Uploading...' : 'Upload'}
      </button>

      <button onClick={onClose}>Cancel</button>
    </div>
  );
};
```

### 2. Visualizacion de Resultados

**Componente:** `AnalysisCard.tsx`

```typescript
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';

interface Analysis {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  images: {
    original: { url: string };
    processed: { url: string };
  };
  risk_assessment: {
    overall_risk_level: 'MINIMO' | 'BAJO' | 'MEDIO' | 'ALTO';
    risk_score: number;
    total_detections: number;
  };
  location: {
    latitude: number;
    longitude: number;
  } | null;
  timestamps: {
    created_at: string;
  };
}

const AnalysisCard = ({ analysis }: { analysis: Analysis }) => {
  const riskColors = {
    MINIMO: 'bg-green-100 text-green-800',
    BAJO: 'bg-blue-100 text-blue-800',
    MEDIO: 'bg-yellow-100 text-yellow-800',
    ALTO: 'bg-red-100 text-red-800'
  };

  return (
    <div className="border rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow">
      {/* Imagen procesada */}
      <img
        src={analysis.images.processed.url}
        alt="Analysis result"
        className="w-full h-48 object-cover rounded-md mb-4"
      />

      {/* Risk badge */}
      <div className="flex items-center gap-2 mb-2">
        <Badge className={riskColors[analysis.risk_assessment.overall_risk_level]}>
          {analysis.risk_assessment.overall_risk_level}
        </Badge>

        <span className="text-sm text-gray-600">
          {analysis.risk_assessment.total_detections} detections
        </span>
      </div>

      {/* Location */}
      {analysis.location && (
        <p className="text-sm text-gray-600 mb-2">
          {analysis.location.latitude.toFixed(4)}, {analysis.location.longitude.toFixed(4)}
        </p>
      )}

      {/* Timestamp */}
      <p className="text-xs text-gray-500 mb-4">
        {new Date(analysis.timestamps.created_at).toLocaleString()}
      </p>

      {/* Actions */}
      <div className="flex gap-2">
        <Button
          onClick={() => window.location.href = `/app/analyses/${analysis.id}`}
          variant="outline"
        >
          View Details
        </Button>

        <Button
          onClick={() => window.open(analysis.images.original.url, '_blank')}
          variant="ghost"
        >
          Original
        </Button>
      </div>
    </div>
  );
};
```

---

## Data Fetching con TanStack Query

### 1. Configuracion de QueryClient

```typescript
// main.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,      // 5 minutos
      cacheTime: 10 * 60 * 1000,     // 10 minutos
      refetchOnWindowFocus: false,
      retry: 1
    }
  }
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>
);
```

### 2. Uso de Queries

**AnalysisPage.tsx:**

```typescript
import { useQuery } from '@tanstack/react-query';
import { analysisApi } from '@/api/client';
import { useState } from 'react';

const AnalysisPage = () => {
  const [page, setPage] = useState(1);
  const [riskFilter, setRiskFilter] = useState<string | null>(null);

  // Query para listar analisis
  const {
    data,
    isLoading,
    isError,
    error,
    refetch
  } = useQuery({
    queryKey: ['analyses', page, riskFilter],
    queryFn: () => analysisApi.getAll({
      page,
      limit: 12,
      risk_level: riskFilter || undefined
    }),
    keepPreviousData: true  // Mantiene datos anteriores mientras carga nuevos
  });

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  if (isError) {
    return <ErrorMessage error={error} />;
  }

  const analyses = data?.data.data || [];

  return (
    <div>
      {/* Filtros */}
      <FilterBar
        riskFilter={riskFilter}
        onRiskFilterChange={setRiskFilter}
      />

      {/* Grid de analisis */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {analyses.map((analysis) => (
          <AnalysisCard key={analysis.id} analysis={analysis} />
        ))}
      </div>

      {/* Paginacion */}
      <Pagination
        currentPage={page}
        onPageChange={setPage}
      />
    </div>
  );
};
```

### 3. Uso de Mutations

**hooks/useAuthMutations.ts:**

```typescript
import { useMutation } from '@tanstack/react-query';
import { authApi } from '@/api/client';
import { useNavigate } from 'react-router-dom';

export const useAuthMutations = () => {
  const navigate = useNavigate();

  const loginMutation = useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      authApi.login(email, password),

    onSuccess: (response) => {
      const { access_token, refresh_token, user } = response.data;

      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('user', JSON.stringify(user));

      navigate('/app/dashboard');
    },

    onError: (error) => {
      console.error('Login failed:', error);
    }
  });

  const logoutMutation = useMutation({
    mutationFn: () => authApi.logout(),

    onSuccess: () => {
      localStorage.clear();
      navigate('/login');
    }
  });

  return {
    login: loginMutation,
    logout: logoutMutation
  };
};
```

---

## Mapa de Calor con Leaflet

### Componente: `HeatMap.tsx`

```typescript
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import { useQuery } from '@tanstack/react-query';
import { analysisApi } from '@/api/client';
import 'leaflet/dist/leaflet.css';

interface Detection {
  id: string;
  latitude: number;
  longitude: number;
  breeding_site_type: string;
  risk_level: 'BAJO' | 'MEDIO' | 'ALTO';
  confidence_score: number;
}

const HeatMap = () => {
  // 1. Obtiene todas las detecciones con ubicacion
  const { data, isLoading } = useQuery({
    queryKey: ['detections-map'],
    queryFn: () => analysisApi.getAll({ limit: 1000 }),
    select: (response) => {
      // Extrae todas las detecciones con ubicacion
      const allDetections: Detection[] = [];

      response.data.data.forEach((analysis: any) => {
        if (analysis.location && analysis.detections) {
          analysis.detections.forEach((det: any) => {
            allDetections.push({
              id: det.id,
              latitude: analysis.location.latitude,
              longitude: analysis.location.longitude,
              breeding_site_type: det.breeding_site_type,
              risk_level: det.risk_level,
              confidence_score: det.confidence_score
            });
          });
        }
      });

      return allDetections;
    }
  });

  if (isLoading) return <div>Loading map...</div>;

  const detections = data || [];

  // 2. Colores por nivel de riesgo
  const riskColors = {
    BAJO: '#3b82f6',    // Azul
    MEDIO: '#eab308',   // Amarillo
    ALTO: '#ef4444'     // Rojo
  };

  // 3. Centro del mapa (Buenos Aires por defecto)
  const center: [number, number] = detections.length > 0
    ? [detections[0].latitude, detections[0].longitude]
    : [-34.603722, -58.381592];

  return (
    <MapContainer
      center={center}
      zoom={13}
      style={{ height: '600px', width: '100%' }}
      className="rounded-lg shadow-md"
    >
      {/* Capa de mapa base */}
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* Marcadores de detecciones */}
      {detections.map((detection) => (
        <CircleMarker
          key={detection.id}
          center={[detection.latitude, detection.longitude]}
          radius={8}
          fillColor={riskColors[detection.risk_level]}
          fillOpacity={0.6}
          color="white"
          weight={2}
        >
          <Popup>
            <div className="p-2">
              <h3 className="font-bold">{detection.breeding_site_type}</h3>
              <p>Risk: {detection.risk_level}</p>
              <p>Confidence: {(detection.confidence_score * 100).toFixed(1)}%</p>
            </div>
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
};

export default HeatMap;
```

---

## State Management con Zustand

### Store de Autenticacion

```typescript
// stores/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;

  setAuth: (user: User, accessToken: string, refreshToken: string) => void;
  clearAuth: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,

      setAuth: (user, accessToken, refreshToken) =>
        set({ user, accessToken, refreshToken }),

      clearAuth: () =>
        set({ user: null, accessToken: null, refreshToken: null }),

      isAuthenticated: () => {
        const { accessToken } = get();
        return !!accessToken;
      }
    }),
    {
      name: 'auth-storage',  // Key en localStorage
    }
  )
);
```

### Store de UI

```typescript
// stores/uiStore.ts
import { create } from 'zustand';

interface UIState {
  uploadModalOpen: boolean;
  sidebarOpen: boolean;

  openUploadModal: () => void;
  closeUploadModal: () => void;
  toggleSidebar: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  uploadModalOpen: false,
  sidebarOpen: true,

  openUploadModal: () => set({ uploadModalOpen: true }),
  closeUploadModal: () => set({ uploadModalOpen: false }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen }))
}));
```

### Uso en Componentes

```typescript
import { useAuthStore } from '@/stores/authStore';
import { useUIStore } from '@/stores/uiStore';

const Header = () => {
  const user = useAuthStore((state) => state.user);
  const clearAuth = useAuthStore((state) => state.clearAuth);
  const openUploadModal = useUIStore((state) => state.openUploadModal);

  const handleLogout = () => {
    clearAuth();
    window.location.href = '/login';
  };

  return (
    <header>
      <p>Welcome, {user?.name}</p>
      <button onClick={openUploadModal}>Upload</button>
      <button onClick={handleLogout}>Logout</button>
    </header>
  );
};
```

---

## Optimizaciones de Performance

### 1. Code Splitting

```typescript
// Lazy loading de paginas
import { lazy, Suspense } from 'react';

const DashboardPage = lazy(() => import('@/pages/app/DashboardPage'));
const AnalysisPage = lazy(() => import('@/pages/app/AnalysisPage'));

const App = () => {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/app/dashboard" element={<DashboardPage />} />
        <Route path="/app/analyses" element={<AnalysisPage />} />
      </Routes>
    </Suspense>
  );
};
```

### 2. Image Lazy Loading

```typescript
const AnalysisImage = ({ src, alt }: { src: string; alt: string }) => {
  return (
    <img
      src={src}
      alt={alt}
      loading="lazy"  // Lazy loading nativo
      className="w-full h-auto"
    />
  );
};
```

### 3. Virtual Scrolling

```typescript
import { useVirtualizer } from '@tanstack/react-virtual';

const AnalysisListVirtual = ({ analyses }: { analyses: Analysis[] }) => {
  const parentRef = React.useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: analyses.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 300,  // Altura estimada de cada item
    overscan: 5  // Items extra a renderizar
  });

  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`
            }}
          >
            <AnalysisCard analysis={analyses[virtualItem.index]} />
          </div>
        ))}
      </div>
    </div>
  );
};
```

### 4. Memoizacion

```typescript
import { memo, useMemo } from 'react';

// Memoiza componente para evitar re-renders innecesarios
const AnalysisCard = memo(({ analysis }: { analysis: Analysis }) => {
  // ... implementacion
});

// Memoiza calculos costosos
const AnalysisStats = ({ analyses }: { analyses: Analysis[] }) => {
  const stats = useMemo(() => {
    const totalDetections = analyses.reduce(
      (sum, a) => sum + a.risk_assessment.total_detections, 0
    );

    const riskDistribution = analyses.reduce((acc, a) => {
      const risk = a.risk_assessment.overall_risk_level;
      acc[risk] = (acc[risk] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return { totalDetections, riskDistribution };
  }, [analyses]);

  return <div>{/* Renderiza stats */}</div>;
};
```

---

## Manejo de Errores

### Error Boundary

```typescript
// components/ui/ErrorBoundary.tsx
import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <h2 className="text-red-800 font-bold">Something went wrong</h2>
          <p className="text-red-600">{this.state.error?.message}</p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="mt-2 px-4 py-2 bg-red-600 text-white rounded"
          >
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

### Uso de Error Boundary

```typescript
// App.tsx
<ErrorBoundary>
  <Routes>
    {/* ... rutas */}
  </Routes>
</ErrorBoundary>
```

---

## Build y Deployment

### Configuracion de Vite

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },

  build: {
    outDir: 'dist',
    sourcemap: true,
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu'],
          'data-vendor': ['@tanstack/react-query', 'axios', 'zustand'],
          'map-vendor': ['leaflet', 'react-leaflet']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  },

  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
});
```

### Variables de Entorno

```bash
# .env.production
VITE_API_URL=https://api.sentrix.com
VITE_YOLO_SERVICE_URL=https://yolo.sentrix.com
```

### Build para Produccion

```bash
# Build
npm run build

# Preview del build
npm run preview

# Analisis de bundle
npm run build -- --mode analyze
```

---

## Referencias

- React Documentation: https://react.dev/
- TypeScript: https://www.typescriptlang.org/
- TanStack Query: https://tanstack.com/query/
- Zustand: https://github.com/pmndrs/zustand
- React Leaflet: https://react-leaflet.js.org/
- Vite: https://vitejs.dev/
- Backend API: ../backend/FUNCIONAMIENTO_BACKEND.md
- YOLO Service: ../yolo-service/FUNCIONAMIENTO_YOLO_SERVICE.md
