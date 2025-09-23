import { api } from './client'
import { apiEndpoints } from '@/lib/config'

export interface DashboardStatistics {
  total_analyses: number
  high_risk_detections: number
  monitored_locations: number
  active_users: number
  monthly_change: {
    total_analyses: number
    high_risk_detections: number
    monitored_locations: number
    active_users: number
  }
}

export interface RiskDistribution {
  name: string
  value: number
  color: string
}

export interface MonthlyAnalysis {
  month: string
  count: number
}

export interface RecentActivity {
  id: number
  type: 'analysis' | 'validation'
  description: string
  risk: 'ALTO' | 'MEDIO' | 'BAJO' | 'MINIMO'
  time: string
  timestamp: string
}

export interface QualityMetrics {
  accuracy: number
  precision: number
  recall: number
  f1_score: number
  processing_time_avg: number
  validated_detections: number
}

export interface ValidationStats {
  pending_validations: number
  validated_today: number
  expert_accuracy: number
  avg_validation_time: number
  top_validators: Array<{
    name: string
    count: number
    accuracy: number
  }>
}

export const reportsApi = {
  getStatistics: async (): Promise<DashboardStatistics> => {
    return api.get(apiEndpoints.reports.statistics)
  },

  getRiskDistribution: async (): Promise<RiskDistribution[]> => {
    return api.get(apiEndpoints.reports.riskDistribution)
  },

  getMonthlyAnalyses: async (): Promise<MonthlyAnalysis[]> => {
    return api.get(apiEndpoints.reports.monthlyAnalyses)
  },

  getRecentActivity: async (limit: number = 10): Promise<RecentActivity[]> => {
    return api.get(`${apiEndpoints.reports.recentActivity}?limit=${limit}`)
  },

  getQualityMetrics: async (): Promise<QualityMetrics> => {
    return api.get(apiEndpoints.reports.qualityMetrics)
  },

  getValidationStats: async (): Promise<ValidationStats> => {
    return api.get(apiEndpoints.reports.validationStats)
  },
}