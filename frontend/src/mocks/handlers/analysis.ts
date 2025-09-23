// Mock handlers for analysis
import { rest } from 'msw'

const mockAnalyses = [
  {
    id: "1",
    status: "completed",
    image_filename: "campo_deportivo_san_juan.jpg",
    image_size_bytes: 3200000,
    location: {
      has_location: true,
      latitude: -11.9756,
      longitude: -77.0132,
      coordinates: "-11.9756,-77.0132",
      altitude_meters: 165,
      location_source: "gps",
      google_maps_url: "https://maps.google.com/?q=-11.9756,-77.0132",
      google_earth_url: "https://earth.google.com/web/search/-11.9756,-77.0132"
    },
    camera_info: {
      camera_make: "Samsung",
      camera_model: "Galaxy S23 Ultra",
      camera_datetime: "2025:09:23 14:25:18",
      camera_software: "Android 14"
    },
    model_used: "dengue_production_v2",
    confidence_threshold: 0.6,
    processing_time_ms: 1850,
    yolo_service_version: "2.0.0",
    risk_assessment: {
      level: "ALTO",
      risk_score: 0.92,
      total_detections: 8,
      high_risk_count: 5,
      medium_risk_count: 2,
      low_risk_count: 1,
      recommendations: ["Inspección urgente: múltiples focos detectados", "Coordinar con autoridades locales", "Programa de limpieza inmediato"]
    },
    detections: [],
    validation_status: "pending_validation",
    processing_queue_position: null,
    image_taken_at: "2025-09-23T14:25:18Z",
    created_at: "2025-09-23T14:25:18Z",
    updated_at: "2025-09-23T14:25:20Z"
  },
  {
    id: "2",
    status: "completed",
    image_filename: "area_media_riesgo.jpg",
    image_size_bytes: 1800000,
    location: {
      has_location: true,
      latitude: -12.0500,
      longitude: -77.0400,
      coordinates: "-12.0500,-77.0400",
      altitude_meters: 145,
      location_source: "gps",
      google_maps_url: "https://maps.google.com/?q=-12.0500,-77.0400",
      google_earth_url: "https://earth.google.com/web/search/-12.0500,-77.0400"
    },
    camera_info: {
      camera_make: "Samsung",
      camera_model: "Galaxy S24",
      camera_datetime: "2025:09:23 10:15:30",
      camera_software: "Android 14"
    },
    model_used: "dengue_production_v2",
    confidence_threshold: 0.5,
    processing_time_ms: 950,
    yolo_service_version: "2.0.0",
    risk_assessment: {
      level: "MEDIO",
      risk_score: 0.65,
      total_detections: 3,
      high_risk_count: 0,
      medium_risk_count: 3,
      low_risk_count: 0,
      recommendations: ["Monitorear área regularmente"]
    },
    detections: [],
    image_taken_at: "2025-09-23T10:15:30Z",
    created_at: "2025-09-23T10:15:30Z",
    updated_at: "2025-09-23T10:15:31Z"
  },
  {
    id: "3",
    status: "completed",
    image_filename: "zona_bajo_riesgo.jpg",
    image_size_bytes: 1500000,
    location: {
      has_location: false,
      latitude: null,
      longitude: null,
      coordinates: null,
      altitude_meters: null,
      location_source: null,
      google_maps_url: null,
      google_earth_url: null
    },
    camera_info: {
      camera_make: "Xiaomi",
      camera_model: "Redmi Note 12",
      camera_datetime: "2025:09:23 11:00:45",
      camera_software: "MIUI 14"
    },
    model_used: "dengue_production_v2",
    confidence_threshold: 0.5,
    processing_time_ms: 800,
    yolo_service_version: "2.0.0",
    risk_assessment: {
      level: "BAJO",
      risk_score: 0.25,
      total_detections: 1,
      high_risk_count: 0,
      medium_risk_count: 0,
      low_risk_count: 1,
      recommendations: ["Mantener área limpia"]
    },
    detections: [],
    image_taken_at: "2025-09-23T11:00:45Z",
    created_at: "2025-09-23T11:00:45Z",
    updated_at: "2025-09-23T11:00:46Z"
  },
  {
    id: "4",
    status: "processing",
    image_filename: "mercado_mayorista_lote_a.jpg",
    image_size_bytes: 4800000,
    location: {
      has_location: true,
      latitude: -12.0625,
      longitude: -77.0893,
      coordinates: "-12.0625,-77.0893",
      altitude_meters: 140,
      location_source: "gps",
      google_maps_url: "https://maps.google.com/?q=-12.0625,-77.0893",
      google_earth_url: "https://earth.google.com/web/search/-12.0625,-77.0893"
    },
    camera_info: {
      camera_make: "Google",
      camera_model: "Pixel 8 Pro",
      camera_datetime: "2025:09:23 15:45:30",
      camera_software: "Android 14"
    },
    model_used: "dengue_production_v2",
    confidence_threshold: 0.5,
    processing_time_ms: null,
    yolo_service_version: "2.0.0",
    risk_assessment: null,
    detections: [],
    validation_status: null,
    processing_queue_position: 2,
    processing_progress: 67,
    image_taken_at: "2025-09-23T15:45:30Z",
    created_at: "2025-09-23T15:45:30Z",
    updated_at: "2025-09-23T15:47:12Z"
  },
  {
    id: "5",
    status: "pending",
    image_filename: "barrio_residencial_callao.jpg",
    image_size_bytes: 2100000,
    location: {
      has_location: false,
      latitude: null,
      longitude: null,
      coordinates: null,
      altitude_meters: null,
      location_source: null,
      google_maps_url: null,
      google_earth_url: null
    },
    camera_info: {
      camera_make: "OnePlus",
      camera_model: "11 Pro",
      camera_datetime: "2025:09:23 16:20:45",
      camera_software: "OxygenOS 14"
    },
    model_used: null,
    confidence_threshold: 0.5,
    processing_time_ms: null,
    yolo_service_version: null,
    risk_assessment: null,
    detections: [],
    validation_status: null,
    processing_queue_position: 1,
    processing_progress: null,
    image_taken_at: "2025-09-23T16:20:45Z",
    created_at: "2025-09-23T16:20:45Z",
    updated_at: "2025-09-23T16:20:45Z"
  },
  {
    id: "6",
    status: "failed",
    image_filename: "imagen_corrupta_error.jpg",
    image_size_bytes: 0,
    location: {
      has_location: false,
      latitude: null,
      longitude: null,
      coordinates: null,
      altitude_meters: null,
      location_source: null,
      google_maps_url: null,
      google_earth_url: null
    },
    camera_info: null,
    model_used: null,
    confidence_threshold: 0.5,
    processing_time_ms: null,
    yolo_service_version: null,
    risk_assessment: null,
    detections: [],
    validation_status: null,
    processing_queue_position: null,
    processing_progress: null,
    error_message: "Archivo corrupto: formato de imagen no válido",
    retry_count: 2,
    image_taken_at: "2025-09-23T16:10:30Z",
    created_at: "2025-09-23T16:10:30Z",
    updated_at: "2025-09-23T16:12:15Z"
  }
]

export const analysisHandlers = [
  rest.get('/api/v1/analyses', (_req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        analyses: mockAnalyses,
        total: mockAnalyses.length,
        limit: 20,
        offset: 0,
        has_next: false
      })
    )
  }),

  rest.get('/api/v1/analyses/recent', (_req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json(mockAnalyses.slice(0, 2))
    )
  }),

  rest.post('/api/v1/analyses', (_req, res, ctx) => {
    const newAnalysis = {
      ...mockAnalyses[0],
      id: String(Date.now()),
      image_filename: "nueva_imagen.jpg",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }

    return res(
      ctx.status(200),
      ctx.json({
        id: newAnalysis.id,
        message: 'Análisis completado',
        analysis: newAnalysis,
        detections: []
      })
    )
  })
]