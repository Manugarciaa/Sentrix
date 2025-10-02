import type { AppConfig } from '@/types'

export const config: AppConfig = {
  api: {
    // En producción usa rutas relativas para aprovechar el proxy de Vercel
    // En desarrollo usa localhost
    baseUrl: import.meta.env.VITE_API_BASE_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000'),
    timeout: 30000, // 30 seconds
  },
  auth: {
    tokenKey: 'sentrix_token',
    refreshTokenKey: 'sentrix_refresh_token',
  },
  features: {
    offlineMode: true,
    realTimeUpdates: true,
    analytics: import.meta.env.PROD,
  },
  ui: {
    defaultPageSize: 20,
    mapDefaultZoom: 12,
    mapDefaultCenter: [-26.8083, -65.2176], // Tucumán, Argentina
  },
}

export const routes = {
  // Rutas públicas
  public: {
    home: '/',
    report: '/report',
    about: '/about',
    contact: '/contact',
    login: '/login',
    register: '/register',
  },
  // Rutas privadas (dashboard)
  app: {
    dashboard: '/app/dashboard',
    analysis: '/app/analysis',
    analysisDetail: (id: string) => `/app/analysis/${id}`,
    uploads: '/app/uploads',
    reports: '/app/reports',
    users: '/app/users',
    settings: '/app/settings',
    profile: '/app/profile',
  },
} as const

export const apiEndpoints = {
  auth: {
    login: '/api/v1/login',
    register: '/api/v1/register',
    refresh: '/api/v1/refresh',
    logout: '/api/v1/logout',
    me: '/api/v1/me',
  },
  analyses: {
    list: '/api/v1/analyses',
    create: '/api/v1/analyses',
    detail: (id: string) => `/api/v1/analyses/${id}`,
    image: (id: string) => `/api/v1/analyses/${id}/image`,
    batch: '/api/v1/analyses/batch',
    export: (id: string) => `/api/v1/analyses/${id}/export`,
    heatmapData: '/api/v1/heatmap-data',
    mapStats: '/api/v1/map-stats',
  },
  detections: {
    byAnalysis: (analysisId: string) => `/api/v1/analyses/${analysisId}/detections`,
    validate: (id: string) => `/api/v1/detections/${id}/validate`,
    pending: '/api/v1/detections/pending',
    batchValidate: '/api/v1/detections/batch-validate',
  },
  reports: {
    // Dashboard ejecutivo
    statistics: '/api/v1/reports/statistics',
    operationalMetrics: '/api/v1/reports/operational-metrics',
    criticalAlerts: '/api/v1/reports/critical-alerts',
    recentActivity: '/api/v1/reports/recent-activity',

    // Sección Reportes (análisis epidemiológico)
    epidemiologicalAnalysis: '/api/v1/reports/epidemiological-analysis',
    riskDistribution: '/api/v1/reports/risk-distribution',
    monthlyAnalyses: '/api/v1/reports/monthly-analyses',
    qualityMetrics: '/api/v1/reports/quality-metrics',
    validationStats: '/api/v1/reports/validation-stats',
  },
  system: {
    health: '/api/v1/health',
    healthDetailed: '/api/v1/health/detailed',
    info: '/api/v1/system/info',
  },
  upload: {
    image: '/api/v1/upload/image',
    batch: '/api/v1/upload/batch',
  },
} as const

export const fileConstraints = {
  maxSize: 50 * 1024 * 1024, // 50MB
  allowedTypes: [
    'image/jpeg',
    'image/jpg',
    'image/png',
    'image/tiff',
    'image/heic',
    'image/heif',
    'image/webp',
    'image/bmp'
  ],
  allowedExtensions: ['.jpg', '.jpeg', '.png', '.tiff', '.heic', '.heif', '.webp', '.bmp'],
}

export const mapConfig = {
  defaultCenter: config.ui.mapDefaultCenter,
  defaultZoom: config.ui.mapDefaultZoom,
  maxZoom: 18,
  minZoom: 5,
  tileLayer: {
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  },
  clusterConfig: {
    maxClusterRadius: 50,
    animate: true,
    showCoverageOnHover: false,
  },
}

export const chartConfig = {
  colors: {
    primary: '#059669',
    secondary: '#f59e0b',
    danger: '#dc2626',
    warning: '#f59e0b',
    success: '#10b981',
    info: '#3b82f6',
  },
  defaultHeight: 300,
}

export const notificationConfig = {
  defaultDuration: 5000, // 5 seconds
  position: 'top-right' as const,
  maxNotifications: 5,
}

export const paginationConfig = {
  defaultPageSize: config.ui.defaultPageSize,
  pageSizeOptions: [10, 20, 50, 100],
}

export const validationMessages = {
  required: 'Este campo es requerido',
  email: 'Ingresa un email válido',
  minLength: (length: number) => `Mínimo ${length} caracteres`,
  maxLength: (length: number) => `Máximo ${length} caracteres`,
  fileSize: 'El archivo es demasiado grande (máximo 50MB)',
  fileType: 'Tipo de archivo no permitido. Formatos soportados: JPG, PNG, TIFF, HEIC, WebP, BMP',
  password: 'La contraseña debe tener al menos 8 caracteres',
  confirmPassword: 'Las contraseñas no coinciden',
}

// Enums sincronizados con shared library
export const riskLevels = {
  ALTO: 'ALTO',
  MEDIO: 'MEDIO',
  BAJO: 'BAJO',
  MINIMO: 'MINIMO',
} as const

export const breedingSiteTypes = {
  BASURA: 'Basura',
  CALLES_MAL_HECHAS: 'Calles mal hechas',
  CHARCOS_CUMULO_AGUA: 'Charcos/Cumulo de agua',
  HUECOS: 'Huecos',
} as const

export const analysisStatus = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
  REQUIRES_VALIDATION: 'requires_validation',
} as const

export const validationStatus = {
  PENDING: 'pending',
  PENDING_VALIDATION: 'pending_validation',
  VALIDATED_POSITIVE: 'validated_positive',
  VALIDATED_NEGATIVE: 'validated_negative',
  REQUIRES_REVIEW: 'requires_review',
} as const

export const userRoles = {
  USER: 'USER',
  ADMIN: 'ADMIN',
  EXPERT: 'EXPERT',
} as const

// Environment variables con valores por defecto
export const env = {
  isDev: import.meta.env.DEV,
  isProd: import.meta.env.PROD,
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000'),
  yoloServiceUrl: import.meta.env.VITE_YOLO_SERVICE_URL || 'http://localhost:8001',
  supabaseUrl: import.meta.env.VITE_SUPABASE_URL,
  supabaseAnonKey: import.meta.env.VITE_SUPABASE_ANON_KEY,
  enableMocking: import.meta.env.VITE_ENABLE_MOCKING === 'true',
  logLevel: import.meta.env.VITE_LOG_LEVEL || 'info',
}