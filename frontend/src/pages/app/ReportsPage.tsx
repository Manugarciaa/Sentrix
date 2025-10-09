import React, { useState, useEffect } from 'react'
import { FileText, Plus, Filter, Download, AlertCircle } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { RadioGroup } from '@/components/ui/RadioGroup'
import { Select } from '@/components/ui/Select'
import { Checkbox } from '@/components/ui/Checkbox'
import { DateRangePicker, DateRange } from '@/components/ui/DateRangePicker'
import { ReportCard, Report } from '@/components/domain/ReportCard'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { EmptyState } from '@/components/domain/EmptyState'
import { config, apiEndpoints } from '@/lib/config'
import type { RiskLevel } from '@/types'

interface ReportConfig {
  type: 'summary' | 'detailed' | 'map' | 'statistics'
  format: 'pdf' | 'csv' | 'json'
  dateRange: DateRange
  filters: {
    risk_level?: RiskLevel
    user_id?: number
    has_gps?: boolean
    validated_only?: boolean
  }
  options: {
    include_images: boolean
    include_map: boolean
    include_charts: boolean
  }
}

const ReportsPage: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [showConfigForm, setShowConfigForm] = useState(false)

  const [reportConfig, setReportConfig] = useState<ReportConfig>({
    type: 'summary',
    format: 'pdf',
    dateRange: {
      from: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      to: new Date().toISOString().split('T')[0],
    },
    filters: {},
    options: {
      include_images: false,
      include_map: true,
      include_charts: true,
    },
  })

  useEffect(() => {
    fetchReports()
  }, [])

  const fetchReports = async () => {
    try {
      setIsLoading(true)

      const response = await fetch(`${config.api.baseUrl}/api/v1/reports/list`)

      if (response.ok) {
        const data = await response.json()
        setReports(data.reports || [])
      }
    } catch (error) {
      console.error('Error fetching reports:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleGenerateReport = async () => {
    try {
      setIsGenerating(true)

      const token = localStorage.getItem('token')
      const response = await fetch(`${config.api.baseUrl}/api/v1/reports/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          type: reportConfig.type,
          format: reportConfig.format,
          date_from: reportConfig.dateRange.from,
          date_to: reportConfig.dateRange.to,
          filters: reportConfig.filters,
          options: reportConfig.options,
        }),
      })

      if (response.ok) {
        const newReport = await response.json()
        setReports([newReport, ...reports])
        setShowConfigForm(false)

        // If ready, auto-download
        if (newReport.status === 'ready' && newReport.download_url) {
          window.open(newReport.download_url, '_blank')
        }
      } else {
        throw new Error('Error al generar el reporte')
      }
    } catch (error) {
      console.error('Error generating report:', error)
      alert('Error al generar el reporte. Por favor intenta nuevamente.')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleDownloadReport = (report: Report) => {
    if (report.download_url) {
      window.open(report.download_url, '_blank')
    }
  }

  const handleViewReport = (report: Report) => {
    if (report.download_url) {
      window.open(report.download_url, '_blank')
    }
  }

  const handleDeleteReport = async (report: Report) => {
    if (!confirm('¿Estás seguro de eliminar este reporte?')) return

    try {
      const response = await fetch(
        `${config.api.baseUrl}/api/v1/reports/${report.id}`,
        { method: 'DELETE' }
      )

      if (response.ok) {
        setReports(reports.filter(r => r.id !== report.id))
      }
    } catch (error) {
      console.error('Error deleting report:', error)
    }
  }

  const getReportTypeDescription = (type: ReportConfig['type']) => {
    switch (type) {
      case 'summary':
        return 'Resumen ejecutivo con métricas clave y gráficos de alto nivel'
      case 'detailed':
        return 'Reporte completo con todos los análisis, detecciones y detalles'
      case 'map':
        return 'Visualización geográfica de detecciones en mapa de calor'
      case 'statistics':
        return 'Análisis estadístico detallado con tablas y gráficos'
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-sm text-gray-600">Cargando reportes...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold text-gray-900">Reportes</h1>
          <p className="text-base text-gray-700 mt-2">
            Genera reportes personalizados de análisis
          </p>
        </div>

        <Button
          onClick={() => setShowConfigForm(!showConfigForm)}
          className="gap-2 bg-gradient-to-r from-primary-600 to-cyan-600"
        >
          <Plus className="h-4 w-4" />
          Nuevo Reporte
        </Button>
      </div>

      {/* Configuration Form */}
      {showConfigForm && (
        <Card className="p-6">
          <div className="flex items-center gap-2 mb-6">
            <Filter className="h-5 w-5 text-gray-700" />
            <h2 className="text-lg font-bold text-gray-900">Configurar Reporte</h2>
          </div>

          <div className="space-y-6">
            {/* Report Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Tipo de Reporte
              </label>
              <RadioGroup
                value={reportConfig.type}
                onValueChange={(value) =>
                  setReportConfig({ ...reportConfig, type: value as ReportConfig['type'] })
                }
              >
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {(['summary', 'detailed', 'map', 'statistics'] as const).map((type) => (
                    <label
                      key={type}
                      className={`flex items-start gap-3 p-4 border-2 rounded-lg cursor-pointer transition-all ${
                        reportConfig.type === type
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <RadioGroupItem value={type} id={type} />
                      <div className="flex-1">
                        <p className="font-medium text-gray-900 capitalize">
                          {type === 'summary' && 'Resumen'}
                          {type === 'detailed' && 'Detallado'}
                          {type === 'map' && 'Mapa'}
                          {type === 'statistics' && 'Estadísticas'}
                        </p>
                        <p className="text-xs text-gray-600 mt-1">
                          {getReportTypeDescription(type)}
                        </p>
                      </div>
                    </label>
                  ))}
                </div>
              </RadioGroup>
            </div>

            {/* Format and Date Range */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Export Format */}
              <div>
                <Select
                  label="Formato de Exportación"
                  options={[
                    { value: 'pdf', label: 'PDF' },
                    { value: 'csv', label: 'CSV (Excel)' },
                    { value: 'json', label: 'JSON (Datos)' },
                  ]}
                  value={reportConfig.format}
                  onChange={(value) =>
                    setReportConfig({ ...reportConfig, format: value as ReportConfig['format'] })
                  }
                />
              </div>

              {/* Date Range */}
              <DateRangePicker
                label="Rango de Fechas"
                value={reportConfig.dateRange}
                onChange={(dateRange) =>
                  setReportConfig({ ...reportConfig, dateRange })
                }
              />
            </div>

            {/* Filters */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-3">Filtros</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Select
                  label="Nivel de Riesgo"
                  options={[
                    { value: '', label: 'Todos' },
                    { value: 'ALTO', label: 'Alto' },
                    { value: 'MEDIO', label: 'Medio' },
                    { value: 'BAJO', label: 'Bajo' },
                  ]}
                  value={reportConfig.filters.risk_level || ''}
                  onChange={(value) =>
                    setReportConfig({
                      ...reportConfig,
                      filters: {
                        ...reportConfig.filters,
                        risk_level: value ? (value as RiskLevel) : undefined,
                      },
                    })
                  }
                />

                <div className="space-y-3 pt-6">
                  <Checkbox
                    label="Solo con GPS"
                    checked={reportConfig.filters.has_gps || false}
                    onChange={(checked) =>
                      setReportConfig({
                        ...reportConfig,
                        filters: { ...reportConfig.filters, has_gps: checked || undefined },
                      })
                    }
                  />
                  <Checkbox
                    label="Solo validados"
                    checked={reportConfig.filters.validated_only || false}
                    onChange={(checked) =>
                      setReportConfig({
                        ...reportConfig,
                        filters: { ...reportConfig.filters, validated_only: checked || undefined },
                      })
                    }
                  />
                </div>
              </div>
            </div>

            {/* Additional Options */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-3">Opciones Adicionales</h3>
              <div className="space-y-3">
                <Checkbox
                  label="Incluir imágenes de análisis"
                  description="Adjuntar imágenes procesadas en el reporte"
                  checked={reportConfig.options.include_images}
                  onChange={(checked) =>
                    setReportConfig({
                      ...reportConfig,
                      options: { ...reportConfig.options, include_images: checked },
                    })
                  }
                />
                <Checkbox
                  label="Incluir mapa de ubicaciones"
                  description="Agregar visualización geográfica de detecciones"
                  checked={reportConfig.options.include_map}
                  onChange={(checked) =>
                    setReportConfig({
                      ...reportConfig,
                      options: { ...reportConfig.options, include_map: checked },
                    })
                  }
                />
                <Checkbox
                  label="Incluir gráficos estadísticos"
                  description="Agregar gráficos de distribución y tendencias"
                  checked={reportConfig.options.include_charts}
                  onChange={(checked) =>
                    setReportConfig({
                      ...reportConfig,
                      options: { ...reportConfig.options, include_charts: checked },
                    })
                  }
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
              <Button
                onClick={() => setShowConfigForm(false)}
                variant="outline"
                disabled={isGenerating}
              >
                Cancelar
              </Button>
              <Button
                onClick={handleGenerateReport}
                disabled={isGenerating || !reportConfig.dateRange.from || !reportConfig.dateRange.to}
                className="bg-gradient-to-r from-primary-600 to-cyan-600"
              >
                {isGenerating ? (
                  <>
                    <LoadingSpinner size="sm" className="mr-2" />
                    Generando...
                  </>
                ) : (
                  <>
                    <FileText className="h-4 w-4 mr-2" />
                    Generar Reporte
                  </>
                )}
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Reports List */}
      <div>
        <h2 className="text-lg font-bold text-gray-900 mb-4">Reportes Generados</h2>

        {reports.length === 0 ? (
          <EmptyState
            icon={FileText}
            title="No hay reportes"
            description="Aún no has generado ningún reporte. Crea uno nuevo para comenzar."
            action={
              <Button
                onClick={() => setShowConfigForm(true)}
                className="bg-gradient-to-r from-primary-600 to-cyan-600"
              >
                <Plus className="h-4 w-4 mr-2" />
                Crear Reporte
              </Button>
            }
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {reports.map((report) => (
              <ReportCard
                key={report.id}
                report={report}
                onDownload={handleDownloadReport}
                onView={handleViewReport}
                onDelete={handleDeleteReport}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default ReportsPage
