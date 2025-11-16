import React from 'react'
import { AlertTriangle, CheckCircle, AlertCircle, Info } from 'lucide-react'
import { cn } from '@/lib/utils'
import { RiskBadge } from './RiskBadge'
import { ProgressBar } from '@/components/ui/ProgressBar'
import type { RiskAssessment } from '@/types'

export interface RiskAssessmentCardProps {
  assessment: RiskAssessment
  className?: string
}

export const RiskAssessmentCard: React.FC<RiskAssessmentCardProps> = ({
  assessment,
  className,
}) => {
  const getRiskIcon = () => {
    switch (assessment.level) {
      case 'ALTO':
        return <AlertTriangle className="h-6 w-6 text-red-600" />
      case 'MEDIO':
        return <AlertCircle className="h-6 w-6 text-amber-600" />
      case 'BAJO':
        return <CheckCircle className="h-6 w-6 text-green-600" />
      default:
        return <Info className="h-6 w-6 text-blue-600" />
    }
  }

  const getRiskGradient = () => {
    switch (assessment.level) {
      case 'ALTO':
        return 'from-red-50 to-red-100 border-red-200'
      case 'MEDIO':
        return 'from-amber-50 to-amber-100 border-amber-200'
      case 'BAJO':
        return 'from-green-50 to-green-100 border-green-200'
      default:
        return 'from-blue-50 to-blue-100 border-blue-200'
    }
  }

  const getRiskDescription = () => {
    switch (assessment.level) {
      case 'ALTO':
        return 'Se requiere acción inmediata. Se han detectado múltiples criaderos de alto riesgo.'
      case 'MEDIO':
        return 'Se recomienda tomar medidas preventivas. Algunos criaderos detectados.'
      case 'BAJO':
        return 'Riesgo controlado. Pocos o ningún criadero de alto riesgo detectado.'
      default:
        return 'No se ha podido determinar el nivel de riesgo.'
    }
  }

  const totalDetections = assessment.total_detections || 0
  const highRiskCount = assessment.high_risk_count || 0
  const mediumRiskCount = assessment.medium_risk_count || 0
  const lowRiskCount = totalDetections - highRiskCount - mediumRiskCount

  const getPercentage = (count: number) => {
    return totalDetections > 0 ? (count / totalDetections) * 100 : 0
  }

  return (
    <div className={cn('bg-white rounded-xl border shadow-sm overflow-hidden', className)}>
      {/* Header */}
      <div className={cn('bg-gradient-to-r p-6 border-b', getRiskGradient())}>
        <div className="flex items-start gap-4">
          <div className="shrink-0">
            {getRiskIcon()}
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h3 className="text-xl font-bold text-gray-900">Evaluación de Riesgo</h3>
              {assessment.level && <RiskBadge level={assessment.level} />}
            </div>
            <p className="text-sm text-gray-700 leading-relaxed">
              {getRiskDescription()}
            </p>
          </div>
        </div>
      </div>

      {/* Risk Score */}
      {assessment.risk_score !== undefined && (
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Puntuación de Riesgo</span>
            <span className="text-2xl font-bold text-gray-900">
              {(assessment.risk_score * 100).toFixed(0)}/100
            </span>
          </div>
          <ProgressBar
            value={assessment.risk_score * 100}
            variant={
              assessment.level === 'ALTO' ? 'danger' :
              assessment.level === 'MEDIO' ? 'warning' : 'success'
            }
            showLabel={false}
          />
        </div>
      )}

      {/* Detection Summary */}
      <div className="p-6">
        <h4 className="text-sm font-semibold text-gray-900 mb-4">Resumen de Detecciones</h4>

        <div className="space-y-4">
          {/* Total */}
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-700">Total de Detecciones</span>
            <span className="text-lg font-bold text-gray-900">{totalDetections}</span>
          </div>

          {/* High Risk */}
          {highRiskCount > 0 && (
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-sm text-gray-700">Alto Riesgo</span>
                <span className="text-sm font-semibold text-red-600">
                  {highRiskCount} ({getPercentage(highRiskCount).toFixed(0)}%)
                </span>
              </div>
              <ProgressBar
                value={getPercentage(highRiskCount)}
                variant="danger"
                showLabel={false}
                size="sm"
              />
            </div>
          )}

          {/* Medium Risk */}
          {mediumRiskCount > 0 && (
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-sm text-gray-700">Riesgo Medio</span>
                <span className="text-sm font-semibold text-amber-600">
                  {mediumRiskCount} ({getPercentage(mediumRiskCount).toFixed(0)}%)
                </span>
              </div>
              <ProgressBar
                value={getPercentage(mediumRiskCount)}
                variant="warning"
                showLabel={false}
                size="sm"
              />
            </div>
          )}

          {/* Low Risk */}
          {lowRiskCount > 0 && (
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-sm text-gray-700">Riesgo Bajo</span>
                <span className="text-sm font-semibold text-green-600">
                  {lowRiskCount} ({getPercentage(lowRiskCount).toFixed(0)}%)
                </span>
              </div>
              <ProgressBar
                value={getPercentage(lowRiskCount)}
                variant="success"
                showLabel={false}
                size="sm"
              />
            </div>
          )}
        </div>
      </div>

      {/* Recommendations */}
      {assessment.recommendations && assessment.recommendations.length > 0 && (
        <div className="px-6 pb-6">
          <h4 className="text-sm font-semibold text-gray-900 mb-3">Recomendaciones</h4>
          <ul className="space-y-2">
            {assessment.recommendations.map((recommendation, index) => (
              <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                <CheckCircle className="h-4 w-4 text-primary-600 shrink-0 mt-0.5" />
                <span>{recommendation}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default RiskAssessmentCard
