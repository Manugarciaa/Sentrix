import React from 'react'
import { FileText, Upload, CheckCircle, Users, Settings } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface TimelineActivity {
  id: string
  type: 'analysis' | 'upload' | 'validation' | 'user' | 'settings'
  title: string
  description: string
  timestamp: string
}

export interface ActivityTimelineProps {
  activities: TimelineActivity[]
  className?: string
}

export const ActivityTimeline: React.FC<ActivityTimelineProps> = ({
  activities,
  className,
}) => {
  const getActivityIcon = (type: TimelineActivity['type']) => {
    switch (type) {
      case 'analysis':
        return FileText
      case 'upload':
        return Upload
      case 'validation':
        return CheckCircle
      case 'user':
        return Users
      case 'settings':
        return Settings
    }
  }

  const getActivityColor = (type: TimelineActivity['type']) => {
    switch (type) {
      case 'analysis':
        return 'bg-blue-100 text-blue-600'
      case 'upload':
        return 'bg-green-100 text-green-600'
      case 'validation':
        return 'bg-purple-100 text-purple-600'
      case 'user':
        return 'bg-amber-100 text-amber-600'
      case 'settings':
        return 'bg-gray-100 text-gray-600'
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Hace un momento'
    if (diffMins < 60) return `Hace ${diffMins} min`
    if (diffHours < 24) return `Hace ${diffHours}h`
    if (diffDays < 7) return `Hace ${diffDays}d`

    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
    })
  }

  if (activities.length === 0) {
    return (
      <div className={cn('text-center py-8', className)}>
        <p className="text-sm text-gray-500">No hay actividad reciente</p>
      </div>
    )
  }

  return (
    <div className={cn('relative', className)}>
      {/* Timeline Line */}
      <div className="absolute left-6 top-4 bottom-4 w-0.5 bg-gray-200" />

      {/* Activities */}
      <div className="space-y-4">
        {activities.map((activity, index) => {
          const Icon = getActivityIcon(activity.type)
          const colorClass = getActivityColor(activity.type)

          return (
            <div key={activity.id} className="relative flex items-start gap-4">
              {/* Icon */}
              <div
                className={cn(
                  'relative z-10 shrink-0 w-12 h-12 rounded-full flex items-center justify-center',
                  colorClass
                )}
              >
                <Icon className="h-5 w-5" />
              </div>

              {/* Content */}
              <div className="flex-1 pt-1">
                <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between gap-2 mb-1">
                    <h4 className="text-sm font-semibold text-gray-900">
                      {activity.title}
                    </h4>
                    <span className="text-xs text-gray-600 shrink-0">
                      {formatTimestamp(activity.timestamp)}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">{activity.description}</p>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default ActivityTimeline
