import React, { useState, useEffect } from 'react'
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts'
import { config, apiEndpoints } from '@/lib/config'
import { Activity, Target, MapPin, Zap } from 'lucide-react'

interface DashboardStats {
  total_analyses: number
  total_detections: number
  area_monitored_km2: number
  model_accuracy: number
  active_zones: number
  risk_distribution: {
    bajo: number
    medio: number
    alto: number
    critico: number
  }
}

const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${config.api.baseUrl}${apiEndpoints.analyses.mapStats}`)
        if (response.ok) {
          const data = await response.json()
          setStats(data)
        }
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        setIsLoading(false)
      }
    }
    fetchData()
  }, [])

  const weekData = [
    { day: 'Lun', value: 45 },
    { day: 'Mar', value: 52 },
    { day: 'Mié', value: 48 },
    { day: 'Jue', value: 65 },
    { day: 'Vie', value: 72 },
    { day: 'Sáb', value: 58 },
    { day: 'Dom', value: 41 },
  ]

  const riskData = stats ? [
    { name: 'Bajo', value: stats.risk_distribution.bajo, color: '#10b981' },
    { name: 'Medio', value: stats.risk_distribution.medio, color: '#f59e0b' },
    { name: 'Alto', value: stats.risk_distribution.alto, color: '#f97316' },
    { name: 'Crítico', value: stats.risk_distribution.critico, color: '#ef4444' },
  ] : []

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500" />
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 mt-2">Resumen general del sistema</p>
        </div>
        <div className="text-sm text-gray-500">
          Actualizado: {new Date().toLocaleDateString('es-ES')}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="relative bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white overflow-hidden">
          <div className="absolute top-0 right-0 opacity-10">
            <Activity className="h-32 w-32" />
          </div>
          <div className="relative">
            <p className="text-blue-100 text-sm font-medium">Análisis Totales</p>
            <p className="text-4xl font-bold mt-2">
              {stats?.total_analyses.toLocaleString() || 0}
            </p>
            <p className="text-blue-100 text-sm mt-4">+12% vs mes anterior</p>
          </div>
        </div>

        <div className="relative bg-gradient-to-br from-red-500 to-red-600 rounded-xl p-6 text-white overflow-hidden">
          <div className="absolute top-0 right-0 opacity-10">
            <Target className="h-32 w-32" />
          </div>
          <div className="relative">
            <p className="text-red-100 text-sm font-medium">Detecciones</p>
            <p className="text-4xl font-bold mt-2">
              {stats?.total_detections.toLocaleString() || 0}
            </p>
            <p className="text-red-100 text-sm mt-4">+8% vs mes anterior</p>
          </div>
        </div>

        <div className="relative bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 text-white overflow-hidden">
          <div className="absolute top-0 right-0 opacity-10">
            <MapPin className="h-32 w-32" />
          </div>
          <div className="relative">
            <p className="text-green-100 text-sm font-medium">Zonas Activas</p>
            <p className="text-4xl font-bold mt-2">
              {stats?.active_zones || 0}
            </p>
            <p className="text-green-100 text-sm mt-4">{stats?.area_monitored_km2 || 0} km² monitoreados</p>
          </div>
        </div>

        <div className="relative bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white overflow-hidden">
          <div className="absolute top-0 right-0 opacity-10">
            <Zap className="h-32 w-32" />
          </div>
          <div className="relative">
            <p className="text-purple-100 text-sm font-medium">Precisión IA</p>
            <p className="text-4xl font-bold mt-2">
              {stats?.model_accuracy || 0}%
            </p>
            <p className="text-purple-100 text-sm mt-4">+2.1% vs mes anterior</p>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Line Chart - Takes 2 columns */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="mb-6">
            <h2 className="text-xl font-bold text-gray-900">Actividad Semanal</h2>
            <p className="text-sm text-gray-500 mt-1">Análisis procesados por día</p>
          </div>
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={weekData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false} />
              <XAxis
                dataKey="day"
                stroke="#9ca3af"
                fontSize={12}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                stroke="#9ca3af"
                fontSize={12}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: 'none',
                  borderRadius: '12px',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                }}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#06b6d4"
                strokeWidth={3}
                dot={{ fill: '#06b6d4', r: 5 }}
                activeDot={{ r: 7 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Risk Distribution Cards */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="mb-6">
            <h2 className="text-xl font-bold text-gray-900">Distribución</h2>
            <p className="text-sm text-gray-500 mt-1">Por nivel de riesgo</p>
          </div>
          <div className="space-y-4">
            {riskData.map((item, index) => {
              const total = riskData.reduce((sum, r) => sum + r.value, 0)
              const percentage = total > 0 ? ((item.value / total) * 100).toFixed(0) : 0
              return (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">{item.name}</span>
                    <span className="text-sm font-bold text-gray-900">{item.value}</span>
                  </div>
                  <div className="relative w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="absolute top-0 left-0 h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${percentage}%`,
                        backgroundColor: item.color
                      }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Bar Chart */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="mb-6">
          <h2 className="text-xl font-bold text-gray-900">Comparativa de Riesgos</h2>
          <p className="text-sm text-gray-500 mt-1">Cantidad de detecciones por nivel</p>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={riskData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false} />
            <XAxis
              dataKey="name"
              stroke="#9ca3af"
              fontSize={12}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              stroke="#9ca3af"
              fontSize={12}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'white',
                border: 'none',
                borderRadius: '12px',
                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
              }}
            />
            <Bar dataKey="value" radius={[8, 8, 0, 0]}>
              {riskData.map((entry, index) => (
                <Bar key={`cell-${index}`} dataKey="value" fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default DashboardPage
