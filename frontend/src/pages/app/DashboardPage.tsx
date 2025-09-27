import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge, getRiskLevelBadge } from '@/components/ui/Badge'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import {
  TrendingUp,
  TrendingDown,
  Shield,
  AlertTriangle,
  MapPin,
  Activity,
  Zap,
  Database,
  Users,
  Trophy,
  Clock,
  CheckCircle,
  XCircle
} from 'lucide-react'
import { reportsApi } from '@/api/reports'

const DashboardPage: React.FC = () => {
  // Combinar datos del dashboard original con mejoras nuevas
  const { data: statistics, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-statistics'],
    queryFn: reportsApi.getStatistics,
    refetchInterval: 30000,
  })

  const { data: riskDistribution, isLoading: riskLoading } = useQuery({
    queryKey: ['risk-distribution'],
    queryFn: reportsApi.getRiskDistribution,
    refetchInterval: 60000,
  })

  const { data: monthlyAnalyses, isLoading: monthlyLoading } = useQuery({
    queryKey: ['monthly-analyses'],
    queryFn: reportsApi.getMonthlyAnalyses,
    refetchInterval: 300000,
  })

  const { data: operationalMetrics, isLoading: operationalLoading } = useQuery({
    queryKey: ['operational-metrics'],
    queryFn: () => fetch('/api/v1/reports/operational-metrics').then(r => r.json()),
    refetchInterval: 15000,
  })

  const { data: criticalAlerts, isLoading: alertsLoading } = useQuery({
    queryKey: ['critical-alerts'],
    queryFn: () => fetch('/api/v1/reports/critical-alerts').then(r => r.json()),
    refetchInterval: 10000,
  })

  const { data: recentActivity, isLoading: activityLoading } = useQuery({
    queryKey: ['recent-activity'],
    queryFn: () => reportsApi.getRecentActivity(5),
    refetchInterval: 10000,
  })

  const loading = statsLoading || riskLoading || monthlyLoading || operationalLoading || alertsLoading || activityLoading

  // Format statistics data for display
  const formatNumber = (num: number): string => {
    return new Intl.NumberFormat('es-PE').format(num)
  }

  const formatChange = (change: number): string => {
    const sign = change >= 0 ? '+' : ''
    return `${sign}${change}%`
  }

  // Métricas principales del dashboard híbrido
  const mainStats = statistics ? [
    {
      title: 'Análisis Totales',
      value: formatNumber(statistics.total_analyses),
      change: formatChange(statistics.monthly_change.total_analyses),
      trend: statistics.monthly_change.total_analyses >= 0 ? 'up' : 'down',
      icon: Activity,
      description: 'Este mes',
    },
    {
      title: 'Detecciones Alto Riesgo',
      value: formatNumber(statistics.critical_alerts),
      change: formatChange(statistics.monthly_change.critical_alerts),
      trend: statistics.monthly_change.critical_alerts >= 0 ? 'up' : 'down',
      icon: AlertTriangle,
      description: 'Últimos 7 días',
    },
    {
      title: 'Áreas Monitoreadas',
      value: formatNumber(statistics.coverage_areas),
      change: formatChange(statistics.monthly_change.coverage_areas),
      trend: statistics.monthly_change.coverage_areas >= 0 ? 'up' : 'down',
      icon: MapPin,
      description: 'Activas',
    },
    {
      title: 'Índice de Riesgo',
      value: `${statistics.dengue_risk_index}/10`,
      change: formatChange(statistics.monthly_change.system_uptime),
      trend: statistics.monthly_change.system_uptime >= 0 ? 'up' : 'down',
      icon: Shield,
      description: 'Epidemiológico',
    },
  ] : []

  if (loading && !statistics) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Cargando dashboard..." />
      </div>
    )
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200'
      case 'warning': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'medium': return 'bg-blue-100 text-blue-800 border-blue-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Vista general del sistema de control de dengue</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-500">Última actualización</p>
          <p className="text-sm font-medium">{new Date().toLocaleString('es-PE')}</p>
        </div>
      </div>

      {/* Critical Alerts Banner */}
      {criticalAlerts && criticalAlerts.length > 0 && (
        <Card className="border-l-4 border-l-red-500">
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              <CardTitle className="text-red-800">Alertas Críticas Activas</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {criticalAlerts.slice(0, 2).map((alert: any) => (
              <div key={alert.id} className={`p-3 rounded-lg border ${getSeverityColor(alert.severity)}`}>
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-medium">{alert.title}</h4>
                    <p className="text-sm mt-1">{alert.description}</p>
                    <p className="text-xs mt-1 opacity-75">{alert.location} • {new Date(alert.timestamp).toLocaleString('es-PE')}</p>
                  </div>
                  {alert.action_required && (
                    <Badge variant="outline" className="text-xs">Acción Requerida</Badge>
                  )}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Main Stats Grid (Estilo original) */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {mainStats.map((stat, index) => {
          const Icon = stat.icon
          const TrendIcon = stat.trend === 'up' ? TrendingUp : TrendingDown
          return (
            <Card key={index}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">
                  {stat.title}
                </CardTitle>
                <Icon className="h-4 w-4 text-gray-400" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
                <div className="flex items-center text-xs text-gray-600">
                  <TrendIcon
                    className={`h-3 w-3 mr-1 ${
                      stat.trend === 'up' ? 'text-green-500' : 'text-red-500'
                    }`}
                  />
                  <span
                    className={
                      stat.trend === 'up' ? 'text-green-600' : 'text-red-600'
                    }
                  >
                    {stat.change}
                  </span>
                  <span className="ml-1">{stat.description}</span>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Charts Grid (Del dashboard original) */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Monthly Analyses Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Análisis por Mes</CardTitle>
            <CardDescription>
              Número de análisis procesados en los últimos 6 meses
            </CardDescription>
          </CardHeader>
          <CardContent>
            {monthlyLoading ? (
              <div className="flex items-center justify-center h-[300px]">
                <LoadingSpinner size="lg" text="Cargando datos..." />
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={monthlyAnalyses}>
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
                  <Bar dataKey="count" fill="#4DD0E1" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        {/* Risk Distribution Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Distribución de Riesgo</CardTitle>
            <CardDescription>
              Clasificación de detecciones por nivel de riesgo
            </CardDescription>
          </CardHeader>
          <CardContent>
            {riskLoading ? (
              <div className="flex items-center justify-center h-[300px]">
                <LoadingSpinner size="lg" text="Cargando datos..." />
              </div>
            ) : (
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
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #E0E0E0',
                      borderRadius: '8px',
                      color: '#212121'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity + System Performance */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Actividad Reciente</CardTitle>
            <CardDescription>
              Últimos análisis y validaciones en el sistema
            </CardDescription>
          </CardHeader>
          <CardContent>
            {activityLoading ? (
              <div className="flex items-center justify-center h-32">
                <LoadingSpinner size="lg" text="Cargando actividad..." />
              </div>
            ) : (
              <div className="space-y-4">
                {recentActivity?.map((activity) => (
                  <div
                    key={activity.id}
                    className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
                  >
                    <div className="flex items-center space-x-4">
                      <div className="h-2 w-2 bg-blue-500 rounded-full" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {activity.description}
                        </p>
                        <p className="text-xs text-gray-500">{activity.time}</p>
                      </div>
                    </div>
                    {activity.risk && (
                      <Badge variant={getRiskLevelBadge(activity.risk) as any}>
                        {activity.risk}
                      </Badge>
                    )}
                  </div>
                )) || (
                  <p className="text-gray-500 text-center py-8">
                    No hay actividad reciente
                  </p>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* System Performance */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-blue-600" />
              Rendimiento del Sistema
            </CardTitle>
            <CardDescription>
              Métricas operacionales en tiempo real
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {operationalMetrics && (
              <>
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                  <div>
                    <p className="text-sm font-medium">Tiempo de Procesamiento</p>
                    <p className="text-xs text-gray-500">Promedio por imagen</p>
                  </div>
                  <div className="text-lg font-bold text-blue-900">{operationalMetrics.processing_performance?.avg_processing_time}s</div>
                </div>
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div>
                    <p className="text-sm font-medium">Tasa de Éxito</p>
                    <p className="text-xs text-gray-500">Análisis completados</p>
                  </div>
                  <div className="text-lg font-bold text-green-900">{operationalMetrics.processing_performance?.success_rate}%</div>
                </div>
                <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                  <div>
                    <p className="text-sm font-medium">Uso de GPU</p>
                    <p className="text-xs text-gray-500">Utilización actual</p>
                  </div>
                  <div className="text-lg font-bold text-purple-900">{operationalMetrics.processing_performance?.gpu_utilization}%</div>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default DashboardPage