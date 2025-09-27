// Utility functions to transform analysis data into map heat data

export interface HeatMapData {
  latitude: number
  longitude: number
  intensity: number
  riskLevel: 'ALTO' | 'MEDIO' | 'BAJO'
  detectionCount: number
  location?: string
  timestamp?: string
  analysisId?: string
}

export interface AnalysisData {
  id: string
  status: string
  image_filename: string
  location: {
    has_location: boolean
    latitude: number | null
    longitude: number | null
    coordinates: string | null
  }
  risk_assessment: {
    level: 'ALTO' | 'MEDIO' | 'BAJO'
    risk_score: number
    total_detections: number
    high_risk_count: number
    medium_risk_count: number
    low_risk_count: number
  } | null
  image_taken_at: string
  created_at: string
}

/**
 * Transform analysis data into heat map format
 */
export const transformAnalysisToHeatData = (analyses: AnalysisData[]): HeatMapData[] => {
  return analyses
    .filter(analysis =>
      analysis.location?.has_location &&
      analysis.location.latitude &&
      analysis.location.longitude &&
      analysis.risk_assessment &&
      analysis.status === 'completed'
    )
    .map(analysis => ({
      latitude: analysis.location.latitude!,
      longitude: analysis.location.longitude!,
      intensity: calculateIntensity(analysis.risk_assessment!),
      riskLevel: analysis.risk_assessment!.level,
      detectionCount: analysis.risk_assessment!.total_detections,
      location: extractLocationFromFilename(analysis.image_filename),
      timestamp: analysis.image_taken_at,
      analysisId: analysis.id
    }))
}

/**
 * Calculate intensity based on risk assessment
 */
const calculateIntensity = (riskAssessment: NonNullable<AnalysisData['risk_assessment']>): number => {
  const { risk_score, total_detections, high_risk_count } = riskAssessment

  // Base intensity from risk score (0-1)
  let intensity = risk_score

  // Boost intensity based on total detections (more detections = higher intensity)
  const detectionBoost = Math.min(total_detections / 10, 0.3) // Max 30% boost
  intensity += detectionBoost

  // Extra boost for high risk detections
  const highRiskBoost = Math.min(high_risk_count / 5, 0.2) // Max 20% boost
  intensity += highRiskBoost

  // Ensure intensity stays between 0 and 1
  return Math.min(Math.max(intensity, 0), 1)
}

/**
 * Extract readable location from filename
 */
const extractLocationFromFilename = (filename: string): string => {
  // Remove extension and replace underscores with spaces
  const name = filename.replace(/\.[^/.]+$/, "").replace(/_/g, ' ')

  // Capitalize first letter of each word
  return name.replace(/\b\w/g, l => l.toUpperCase())
}

/**
 * Filter heat data by date range
 */
export const filterByDateRange = (
  data: HeatMapData[],
  startDate: Date,
  endDate: Date
): HeatMapData[] => {
  return data.filter(point => {
    if (!point.timestamp) return true
    const pointDate = new Date(point.timestamp)
    return pointDate >= startDate && pointDate <= endDate
  })
}

/**
 * Filter heat data by risk level
 */
export const filterByRiskLevel = (
  data: HeatMapData[],
  riskLevels: ('ALTO' | 'MEDIO' | 'BAJO')[]
): HeatMapData[] => {
  return data.filter(point => riskLevels.includes(point.riskLevel))
}

/**
 * Get statistics from heat data
 */
export const getHeatDataStats = (data: HeatMapData[]) => {
  const totalPoints = data.length
  const riskCounts = {
    ALTO: data.filter(p => p.riskLevel === 'ALTO').length,
    MEDIO: data.filter(p => p.riskLevel === 'MEDIO').length,
    BAJO: data.filter(p => p.riskLevel === 'BAJO').length
  }

  const totalDetections = data.reduce((sum, point) => sum + point.detectionCount, 0)
  const avgIntensity = data.length > 0
    ? data.reduce((sum, point) => sum + point.intensity, 0) / data.length
    : 0

  return {
    totalPoints,
    riskCounts,
    totalDetections,
    avgIntensity
  }
}

/**
 * Generate mock heat data for testing (based on Tucumán, Argentina coordinates)
 */
export const generateMockHeatData = (): HeatMapData[] => {
  const baseLocations = [
    { lat: -26.8083, lng: -65.2176, name: "Centro de Tucumán" },
    { lat: -26.7906, lng: -65.2164, name: "Barrio Norte" },
    { lat: -26.8156, lng: -65.2042, name: "Yerba Buena" },
    { lat: -26.8294, lng: -65.2356, name: "Villa Mariano Moreno" },
    { lat: -26.7789, lng: -65.2089, name: "Las Talitas" },
    { lat: -26.8445, lng: -65.2198, name: "Barrio Sur" },
    { lat: -26.8012, lng: -65.1956, name: "Tafí Viejo" },
    { lat: -26.7654, lng: -65.2445, name: "Banda del Río Salí" },
    { lat: -26.8567, lng: -65.2078, name: "Villa Carmela" },
    { lat: -26.7890, lng: -65.2344, name: "Alderetes" }
  ]

  const riskLevels: ('ALTO' | 'MEDIO' | 'BAJO')[] = ['ALTO', 'MEDIO', 'BAJO']

  return baseLocations.map((location, index) => {
    const riskLevel = riskLevels[index % 3]
    const detectionCount = Math.floor(Math.random() * 15) + 1

    return {
      latitude: location.lat + (Math.random() - 0.5) * 0.01, // Add some random variance
      longitude: location.lng + (Math.random() - 0.5) * 0.01,
      intensity: riskLevel === 'ALTO' ? 0.8 + Math.random() * 0.2 :
                riskLevel === 'MEDIO' ? 0.4 + Math.random() * 0.4 :
                Math.random() * 0.4,
      riskLevel,
      detectionCount,
      location: location.name,
      timestamp: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
      analysisId: `mock-${index + 1}`
    }
  })
}