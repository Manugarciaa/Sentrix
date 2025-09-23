import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { reportsApi } from '@/api/reports'
// import { analysesApi } from '@/api/analyses'
import {
  // BarChart,
  // Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  // LineChart,
  // Line,
  Area,
  AreaChart
} from 'recharts'
import {
  Download,
  FileText,
  FileSpreadsheet,
  // Calendar,
  // TrendingUp,
  // MapPin,
  // Camera,
  AlertTriangle,
  CheckCircle,
  Users,
  Activity,
  // Filter,
  RefreshCw
} from 'lucide-react'

type ExportFormat = 'json' | 'csv' | 'pdf'
type DateRange = '7d' | '30d' | '90d' | '1y' | 'all'

const ReportsPage: React.FC = () => {
  const [selectedRange, setSelectedRange] = useState<DateRange>('30d')
  const [isExporting, setIsExporting] = useState<ExportFormat | null>(null)
  // const [exportFilter, setExportFilter] = useState({
  //   riskLevel: '',
  //   hasGps: null as boolean | null,
  //   cameraMake: '',
  // })

  // Fetch epidemiological analysis data
  const { data: epidemiologicalData, isLoading: epidemiologicalLoading } = useQuery({
    queryKey: ['epidemiological-analysis'],
    queryFn: () => fetch('/api/v1/reports/epidemiological-analysis').then(r => r.json()),
    refetchInterval: 300000,
  })

  // Fetch risk distribution for breeding sites
  const { data: riskDistribution, isLoading: riskLoading } = useQuery({
    queryKey: ['risk-distribution'],
    queryFn: reportsApi.getRiskDistribution,
    refetchInterval: 60000,
  })

  const loading = epidemiologicalLoading || riskLoading

  // Export functions
  const handleExport = async (format: ExportFormat) => {
    setIsExporting(format)
    try {
      switch (format) {
        case 'json':
          await exportAsJSON()
          break
        case 'csv':
          await exportAsCSV()
          break
        case 'pdf':
          await exportAsPDF()
          break
      }
    } catch (error) {
      console.error('Export failed:', error)
    } finally {
      setIsExporting(null)
    }
  }

  const exportAsJSON = async () => {
    const data = {
      generated_at: new Date().toISOString(),
      date_range: selectedRange,
      statistics,
      risk_distribution: riskDistribution,
      monthly_analyses: monthlyAnalyses,
      quality_metrics: qualityMetrics,
      validation_stats: validationStats,
    }

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `sentrix-report-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const exportAsCSV = async () => {
    const csvData = [
      ['Sentrix Analysis Report', ''],
      ['Generated At', new Date().toLocaleString()],
      ['Date Range', selectedRange],
      [''],
      ['Statistics', ''],
      ['Total Analyses', statistics?.total_analyses || 0],
      ['High Risk Detections', statistics?.high_risk_detections || 0],
      ['Monitored Locations', statistics?.monitored_locations || 0],
      ['Active Users', statistics?.active_users || 0],
      [''],
      ['Monthly Analyses', ''],
      ...(monthlyAnalyses?.map(item => [item.month, item.count]) || []),
      [''],
      ['Quality Metrics', ''],
      ['Accuracy', qualityMetrics?.accuracy || 0],
      ['Precision', qualityMetrics?.precision || 0],
      ['Recall', qualityMetrics?.recall || 0],
      ['F1 Score', qualityMetrics?.f1_score || 0],
    ]

    const csvContent = csvData.map(row => row.join(',')).join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `sentrix-report-${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const exportAsPDF = async () => {
    // In a real implementation, you would use a library like jsPDF or html2pdf
    alert('PDF export would be implemented using jsPDF or a similar library')
  }

  // Data transformations for charts
  const formatPercentage = (value: number) => `${value.toFixed(1)}%`
  const formatTime = (seconds: number) => `${seconds.toFixed(1)}s`

  // Trend data simulation (in real app, this would come from API)
  const trendData = monthlyAnalyses?.map((item, index) => ({
    ...item,
    trend: index > 0 ? item.count - (monthlyAnalyses[index - 1]?.count || 0) : 0,
    cumulative: monthlyAnalyses.slice(0, index + 1).reduce((sum, i) => sum + i.count, 0)
  })) || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Análisis Epidemiológico</h1>
          <p className="text-gray-600">
            Tendencias, correlaciones y análisis científico de los datos de vigilancia
          </p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={selectedRange}
            onChange={(e) => setSelectedRange(e.target.value as DateRange)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="7d">Últimos 7 días</option>
            <option value="30d">Últimos 30 días</option>
            <option value="90d">Últimos 90 días</option>
            <option value="1y">Último año</option>
            <option value="all">Todo</option>
          </select>
          <Button variant="outline" className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4" />
            Actualizar
          </Button>
        </div>
      </div>

      {/* Export Options */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Download className="h-5 w-5" />
            Exportar Reportes
          </CardTitle>
          <CardDescription>
            Descarga informes completos en diferentes formatos
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Button
              onClick={() => handleExport('json')}
              disabled={isExporting === 'json'}
              className="flex items-center gap-2"
            >
              {isExporting === 'json' ? (
                <LoadingSpinner size="sm" />
              ) : (
                <FileText className="h-4 w-4" />
              )}
              Exportar JSON
            </Button>
            <Button
              onClick={() => handleExport('csv')}
              disabled={isExporting === 'csv'}
              variant="outline"
              className="flex items-center gap-2"
            >
              {isExporting === 'csv' ? (
                <LoadingSpinner size="sm" />
              ) : (
                <FileSpreadsheet className="h-4 w-4" />
              )}
              Exportar CSV
            </Button>
            <Button
              onClick={() => handleExport('pdf')}
              disabled={isExporting === 'pdf'}
              variant="outline"
              className="flex items-center gap-2"
            >
              {isExporting === 'pdf' ? (
                <LoadingSpinner size="sm" />
              ) : (
                <FileText className="h-4 w-4" />
              )}
              Exportar PDF
            </Button>
          </div>
        </CardContent>
      </Card>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" text="Cargando datos del reporte..." />
        </div>
      ) : (
        <>
          {/* Key Performance Indicators */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Activity className="h-8 w-8 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Total Análisis</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {statistics?.total_analyses?.toLocaleString() || 0}
                    </p>
                    <p className="text-xs text-green-600">
                      +{statistics?.monthly_change?.total_analyses || 0}% este mes
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <AlertTriangle className="h-8 w-8 text-red-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Alto Riesgo</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {statistics?.high_risk_detections || 0}
                    </p>
                    <p className="text-xs text-red-600">
                      {statistics?.monthly_change?.high_risk_detections || 0}% este mes
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <CheckCircle className="h-8 w-8 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Precisión</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatPercentage(qualityMetrics?.accuracy || 0)}
                    </p>
                    <p className="text-xs text-gray-500">Modelo actual</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Users className="h-8 w-8 text-purple-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Validaciones</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {validationStats?.validated_today || 0}
                    </p>
                    <p className="text-xs text-gray-500">Hoy</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Charts Grid */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {/* Monthly Trend */}
            <Card>
              <CardHeader>
                <CardTitle>Tendencia de Análisis</CardTitle>
                <CardDescription>
                  Evolución mensual de análisis procesados
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={trendData}>
                    <defs>
                      <linearGradient id="colorAnalyses" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#4DD0E1" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#4DD0E1" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#EEEEEE" />
                    <XAxis dataKey="month" tick={{ fill: '#616161', fontSize: 12 }} />
                    <YAxis tick={{ fill: '#616161', fontSize: 12 }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'white',
                        border: '1px solid #E0E0E0',
                        borderRadius: '8px',
                        color: '#212121'
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="count"
                      stroke="#4DD0E1"
                      fillOpacity={1}
                      fill="url(#colorAnalyses)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Risk Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Distribución de Riesgo</CardTitle>
                <CardDescription>
                  Clasificación por nivel de riesgo detectado
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={riskDistribution}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {riskDistribution?.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Quality Metrics */}
            <Card>
              <CardHeader>
                <CardTitle>Métricas de Calidad</CardTitle>
                <CardDescription>
                  Rendimiento del modelo de detección
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Precisión</span>
                    <span className="font-bold">{formatPercentage(qualityMetrics?.precision || 0)}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${qualityMetrics?.precision || 0}%` }}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Recall</span>
                    <span className="font-bold">{formatPercentage(qualityMetrics?.recall || 0)}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full"
                      style={{ width: `${qualityMetrics?.recall || 0}%` }}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">F1-Score</span>
                    <span className="font-bold">{formatPercentage(qualityMetrics?.f1_score || 0)}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-purple-600 h-2 rounded-full"
                      style={{ width: `${qualityMetrics?.f1_score || 0}%` }}
                    />
                  </div>

                  <div className="pt-4 border-t">
                    <div className="flex items-center justify-between text-sm">
                      <span>Tiempo promedio de procesamiento:</span>
                      <span className="font-medium">{formatTime(qualityMetrics?.processing_time_avg || 0)}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span>Detecciones validadas:</span>
                      <span className="font-medium">{formatPercentage(qualityMetrics?.validated_detections || 0)}</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Top Validators */}
            <Card>
              <CardHeader>
                <CardTitle>Validadores Principales</CardTitle>
                <CardDescription>
                  Expertos con mayor actividad de validación
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {validationStats?.top_validators?.map((validator, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <span className="text-sm font-bold text-blue-600">{index + 1}</span>
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">{validator.name}</p>
                          <p className="text-sm text-gray-500">{validator.count} validaciones</p>
                        </div>
                      </div>
                      <Badge variant="outline">
                        {formatPercentage(validator.accuracy)}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Summary Statistics */}
          <Card>
            <CardHeader>
              <CardTitle>Resumen del Período</CardTitle>
              <CardDescription>
                Estadísticas consolidadas para el rango seleccionado
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600">
                    {statistics?.monitored_locations || 0}
                  </p>
                  <p className="text-sm text-gray-600">Ubicaciones Monitoreadas</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">
                    {validationStats?.pending_validations || 0}
                  </p>
                  <p className="text-sm text-gray-600">Validaciones Pendientes</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-purple-600">
                    {formatTime(validationStats?.avg_validation_time || 0)}
                  </p>
                  <p className="text-sm text-gray-600">Tiempo Promedio de Validación</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}

export default ReportsPage