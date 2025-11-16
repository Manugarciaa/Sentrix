import type { AnalysisFilters, UserFilters, UserRole } from '@/types'

/**
 * Hierarchical query key patterns for React Query cache management
 * 
 * This structure follows the recommended pattern from React Query docs:
 * - Use arrays for query keys
 * - Make keys hierarchical (general to specific)
 * - Include all variables that affect the query result
 * - Use consistent patterns across the application
 */

// Auth Query Keys
export const authKeys = {
  // Base key for all auth-related queries
  all: ['auth'] as const,
  
  // User profile queries
  profile: () => [...authKeys.all, 'profile'] as const,
  me: () => [...authKeys.profile(), 'me'] as const,
  
  // Permission queries
  permissions: () => [...authKeys.all, 'permissions'] as const,
  userPermissions: (userId: string) => [...authKeys.permissions(), userId] as const,
} as const

// Analysis Query Keys
export const analysisKeys = {
  // Base key for all analysis-related queries
  all: ['analyses'] as const,
  
  // List queries
  lists: () => [...analysisKeys.all, 'list'] as const,
  list: (filters?: AnalysisFilters) => [...analysisKeys.lists(), filters] as const,
  
  // Detail queries
  details: () => [...analysisKeys.all, 'detail'] as const,
  detail: (id: string) => [...analysisKeys.details(), id] as const,
  
  // Image queries
  images: () => [...analysisKeys.all, 'image'] as const,
  image: (id: string) => [...analysisKeys.images(), id] as const,
  
  // Detection queries
  detections: () => [...analysisKeys.all, 'detections'] as const,
  detectionsByAnalysis: (analysisId: string) => [...analysisKeys.detections(), 'byAnalysis', analysisId] as const,
  pendingDetections: () => [...analysisKeys.detections(), 'pending'] as const,
  
  // Map data queries
  mapData: () => [...analysisKeys.all, 'mapData'] as const,
  heatmapData: (filters?: AnalysisFilters) => [...analysisKeys.mapData(), 'heatmap', filters] as const,
  mapStats: (filters?: AnalysisFilters) => [...analysisKeys.mapData(), 'stats', filters] as const,
  
  // Export queries
  exports: () => [...analysisKeys.all, 'export'] as const,
  export: (id: string, format: string) => [...analysisKeys.exports(), id, format] as const,
} as const

// User Query Keys
export const userKeys = {
  // Base key for all user-related queries
  all: ['users'] as const,
  
  // List queries
  lists: () => [...userKeys.all, 'list'] as const,
  list: (filters?: UserFilters) => [...userKeys.lists(), filters] as const,
  
  // Detail queries
  details: () => [...userKeys.all, 'detail'] as const,
  detail: (id: string) => [...userKeys.details(), id] as const,
  
  // Statistics queries
  stats: () => [...userKeys.all, 'stats'] as const,
  userStats: () => [...userKeys.stats(), 'overview'] as const,
  
  // Activity queries
  activities: () => [...userKeys.all, 'activity'] as const,
  userActivity: (id: string, filters?: { date_from?: string; date_to?: string; activity_type?: string }) => 
    [...userKeys.activities(), id, filters] as const,
  
  // Role-based queries
  byRole: (role: UserRole) => [...userKeys.all, 'byRole', role] as const,
} as const

// Report Query Keys
export const reportKeys = {
  // Base key for all report-related queries
  all: ['reports'] as const,
  
  // Dashboard reports
  dashboard: () => [...reportKeys.all, 'dashboard'] as const,
  statistics: () => [...reportKeys.dashboard(), 'statistics'] as const,
  operationalMetrics: () => [...reportKeys.dashboard(), 'operationalMetrics'] as const,
  criticalAlerts: () => [...reportKeys.dashboard(), 'criticalAlerts'] as const,
  recentActivity: () => [...reportKeys.dashboard(), 'recentActivity'] as const,
  
  // Epidemiological reports
  epidemiological: () => [...reportKeys.all, 'epidemiological'] as const,
  epidemiologicalAnalysis: (filters?: AnalysisFilters) => [...reportKeys.epidemiological(), 'analysis', filters] as const,
  riskDistribution: (filters?: AnalysisFilters) => [...reportKeys.epidemiological(), 'riskDistribution', filters] as const,
  monthlyAnalyses: (filters?: AnalysisFilters) => [...reportKeys.epidemiological(), 'monthlyAnalyses', filters] as const,
  
  // Quality reports
  quality: () => [...reportKeys.all, 'quality'] as const,
  qualityMetrics: (filters?: AnalysisFilters) => [...reportKeys.quality(), 'metrics', filters] as const,
  validationStats: (filters?: AnalysisFilters) => [...reportKeys.quality(), 'validationStats', filters] as const,
} as const

// System Query Keys
export const systemKeys = {
  // Base key for all system-related queries
  all: ['system'] as const,
  
  // Health checks
  health: () => [...systemKeys.all, 'health'] as const,
  healthCheck: () => [...systemKeys.health(), 'basic'] as const,
  healthDetailed: () => [...systemKeys.health(), 'detailed'] as const,
  
  // System info
  info: () => [...systemKeys.all, 'info'] as const,
  systemInfo: () => [...systemKeys.info(), 'overview'] as const,
} as const

// Upload Query Keys
export const uploadKeys = {
  // Base key for all upload-related queries
  all: ['uploads'] as const,
  
  // Upload progress tracking (for optimistic updates)
  progress: () => [...uploadKeys.all, 'progress'] as const,
  uploadProgress: (uploadId: string) => [...uploadKeys.progress(), uploadId] as const,
  
  // Batch upload tracking
  batch: () => [...uploadKeys.all, 'batch'] as const,
  batchProgress: (batchId: string) => [...uploadKeys.batch(), batchId] as const,
} as const

/**
 * Query Key Utilities
 * Helper functions for cache invalidation and management
 */
export const queryKeyUtils = {
  // Invalidate all queries for a specific entity
  invalidateAuth: () => authKeys.all,
  invalidateAnalyses: () => analysisKeys.all,
  invalidateUsers: () => userKeys.all,
  invalidateReports: () => reportKeys.all,
  invalidateSystem: () => systemKeys.all,
  invalidateUploads: () => uploadKeys.all,
  
  // Invalidate specific query patterns
  invalidateAnalysisList: () => analysisKeys.lists(),
  invalidateAnalysisDetail: (id: string) => analysisKeys.detail(id),
  invalidateUserList: () => userKeys.lists(),
  invalidateUserDetail: (id: string) => userKeys.detail(id),
  
  // Invalidate related queries when data changes
  invalidateAfterAnalysisCreate: () => [
    analysisKeys.lists(),
    reportKeys.dashboard(),
    reportKeys.epidemiological(),
  ],
  
  invalidateAfterAnalysisUpdate: (id: string) => [
    analysisKeys.detail(id),
    analysisKeys.lists(),
    reportKeys.dashboard(),
  ],
  
  invalidateAfterAnalysisDelete: (id: string) => [
    analysisKeys.detail(id),
    analysisKeys.lists(),
    reportKeys.dashboard(),
    reportKeys.epidemiological(),
  ],
  
  invalidateAfterUserCreate: () => [
    userKeys.lists(),
    userKeys.stats(),
  ],
  
  invalidateAfterUserUpdate: (id: string) => [
    userKeys.detail(id),
    userKeys.lists(),
    userKeys.stats(),
  ],
  
  invalidateAfterUserDelete: (id: string) => [
    userKeys.detail(id),
    userKeys.lists(),
    userKeys.stats(),
  ],
  
  invalidateAfterDetectionValidation: (analysisId: string) => [
    analysisKeys.detail(analysisId),
    analysisKeys.detectionsByAnalysis(analysisId),
    analysisKeys.pendingDetections(),
    reportKeys.quality(),
  ],
  
  invalidateAfterProfileUpdate: () => [
    authKeys.me(),
    authKeys.profile(),
  ],
}

/**
 * Type-safe query key factories
 * These ensure that query keys are properly typed and consistent
 */
export type AuthQueryKeys = typeof authKeys
export type AnalysisQueryKeys = typeof analysisKeys
export type UserQueryKeys = typeof userKeys
export type ReportQueryKeys = typeof reportKeys
export type SystemQueryKeys = typeof systemKeys
export type UploadQueryKeys = typeof uploadKeys

// Export all query keys as a single object for convenience
export const queryKeys = {
  auth: authKeys,
  analyses: analysisKeys,
  users: userKeys,
  reports: reportKeys,
  system: systemKeys,
  uploads: uploadKeys,
  utils: queryKeyUtils,
} as const

export default queryKeys