// Mock handlers for reports
import { rest } from 'msw'

export const reportsHandlers = [
  // Dashboard ejecutivo - métricas de alto nivel
  rest.get('/api/v1/reports/statistics', (_req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        // Métricas principales del último mes
        total_analyses: 1247,
        critical_alerts: 23,
        coverage_areas: 45,
        system_uptime: 99.8,
        monthly_change: {
          total_analyses: 18,
          critical_alerts: -12,
          coverage_areas: 7,
          system_uptime: 0.2
        },
        // Métricas epidemiológicas
        dengue_risk_index: 7.2, // 0-10 escala
        hotspots_identified: 8,
        prevention_score: 82, // 0-100
        community_engagement: 76 // 0-100
      })
    )
  }),

  // Métricas operacionales para dashboard
  rest.get('/api/v1/reports/operational-metrics', (_req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        processing_performance: {
          avg_processing_time: 1.2, // segundos
          success_rate: 98.5, // porcentaje
          queue_length: 3,
          gpu_utilization: 75 // porcentaje
        },
        storage_metrics: {
          total_images: 15420,
          storage_used_gb: 284.7,
          storage_limit_gb: 1000,
          backup_status: "healthy"
        },
        user_activity: {
          active_today: 28,
          sessions_this_week: 156,
          expert_validations_pending: 12
        }
      })
    )
  }),

  rest.get('/api/v1/reports/risk-distribution', (_req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        { name: 'Alto', value: 52, color: '#dc2626' },
        { name: 'Medio', value: 89, color: '#f59e0b' },
        { name: 'Bajo', value: 74, color: '#10b981' },
        { name: 'Mínimo', value: 30, color: '#6b7280' }
      ])
    )
  }),

  rest.get('/api/v1/reports/monthly-analyses', (_req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        { month: 'Abr', count: 28 },
        { month: 'May', count: 35 },
        { month: 'Jun', count: 42 },
        { month: 'Jul', count: 38 },
        { month: 'Ago', count: 48 },
        { month: 'Sep', count: 54 }
      ])
    )
  }),

  // Alertas críticas para dashboard
  rest.get('/api/v1/reports/critical-alerts', (_req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        {
          id: 1,
          type: 'hotspot',
          title: 'Nuevo foco de riesgo detectado',
          description: 'Zona San Juan - 15 detecciones alto riesgo en 24h',
          severity: 'critical',
          location: 'San Juan, Lima',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          action_required: true
        },
        {
          id: 2,
          type: 'system',
          title: 'GPU utilization alta',
          description: 'Procesamiento al 95% de capacidad por 30min',
          severity: 'warning',
          location: 'Sistema',
          timestamp: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
          action_required: false
        },
        {
          id: 3,
          type: 'validation',
          title: 'Validaciones pendientes acumuladas',
          description: '23 detecciones esperando validación experta',
          severity: 'medium',
          location: 'Sistema',
          timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
          action_required: true
        }
      ])
    )
  }),

  // Actividad reciente (solo para dashboard ejecutivo)
  rest.get('/api/v1/reports/recent-activity', (_req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        {
          id: 1,
          type: 'milestone',
          description: '1000 análisis completados este mes',
          time: 'Hace 2 horas',
          icon: 'trophy'
        },
        {
          id: 2,
          type: 'coverage',
          description: 'Nueva área de cobertura: Villa El Salvador',
          time: 'Hace 1 día',
          icon: 'map'
        },
        {
          id: 3,
          type: 'expert',
          description: 'Dr. García validó 25 detecciones',
          time: 'Hace 2 días',
          icon: 'user'
        }
      ])
    )
  }),

  // Datos específicos para sección Reportes (análisis epidemiológico)
  rest.get('/api/v1/reports/epidemiological-analysis', (_req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        temporal_trends: [
          { period: 'Ene', detections: 45, risk_score: 6.2 },
          { period: 'Feb', detections: 52, risk_score: 6.8 },
          { period: 'Mar', detections: 38, risk_score: 5.9 },
          { period: 'Apr', detections: 67, risk_score: 7.3 },
          { period: 'May', detections: 89, risk_score: 8.1 },
          { period: 'Jun', detections: 94, risk_score: 8.4 }
        ],
        geographic_distribution: [
          { district: 'San Juan de Lurigancho', detections: 156, population: 1200000, incidence: 13.0 },
          { district: 'Villa El Salvador', detections: 89, population: 463000, incidence: 19.2 },
          { district: 'Ate', detections: 67, population: 630000, incidence: 10.6 },
          { district: 'Comas', detections: 54, population: 520000, incidence: 10.4 }
        ],
        breeding_site_analysis: [
          { type: 'Acumulaciones de agua', count: 89, percentage: 35.2, trend: 'increasing' },
          { type: 'Basura', count: 76, percentage: 30.1, trend: 'stable' },
          { type: 'Calles deterioradas', count: 52, percentage: 20.6, trend: 'decreasing' },
          { type: 'Huecos', count: 36, percentage: 14.1, trend: 'stable' }
        ],
        risk_correlation: {
          weather_correlation: 0.78,
          population_density_correlation: 0.65,
          socioeconomic_correlation: -0.54,
          infrastructure_correlation: -0.72
        }
      })
    )
  }),

  rest.get('/api/v1/reports/quality-metrics', (_req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        accuracy: 94.2,
        precision: 91.8,
        recall: 89.5,
        f1_score: 90.6,
        processing_time_avg: 1250,
        validated_detections: 156
      })
    )
  }),

  rest.get('/api/v1/reports/validation-stats', (_req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        pending_validations: 23,
        validated_today: 18,
        expert_accuracy: 96.8,
        avg_validation_time: 45,
        top_validators: [
          { name: 'Dr. María González', count: 45, accuracy: 98.2 },
          { name: 'Dr. Carlos Ruiz', count: 38, accuracy: 96.1 },
          { name: 'Dra. Ana Martínez', count: 32, accuracy: 97.5 }
        ]
      })
    )
  })
]