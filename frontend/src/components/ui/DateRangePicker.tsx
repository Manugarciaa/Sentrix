import React, { useState } from 'react'
import { Calendar, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Input } from './Input'
import { Button } from './Button'

export interface DateRange {
  from?: string
  to?: string
}

export interface DateRangePickerProps {
  value: DateRange
  onChange: (range: DateRange) => void
  label?: string
  minDate?: string
  maxDate?: string
  presets?: Array<{ label: string; getValue: () => DateRange }>
  className?: string
}

const defaultPresets = [
  {
    label: 'Últimos 7 días',
    getValue: () => {
      const to = new Date()
      const from = new Date()
      from.setDate(from.getDate() - 7)
      return {
        from: from.toISOString().split('T')[0],
        to: to.toISOString().split('T')[0],
      }
    },
  },
  {
    label: 'Últimos 30 días',
    getValue: () => {
      const to = new Date()
      const from = new Date()
      from.setDate(from.getDate() - 30)
      return {
        from: from.toISOString().split('T')[0],
        to: to.toISOString().split('T')[0],
      }
    },
  },
  {
    label: 'Último mes',
    getValue: () => {
      const to = new Date()
      const from = new Date()
      from.setMonth(from.getMonth() - 1)
      return {
        from: from.toISOString().split('T')[0],
        to: to.toISOString().split('T')[0],
      }
    },
  },
  {
    label: 'Últimos 3 meses',
    getValue: () => {
      const to = new Date()
      const from = new Date()
      from.setMonth(from.getMonth() - 3)
      return {
        from: from.toISOString().split('T')[0],
        to: to.toISOString().split('T')[0],
      }
    },
  },
  {
    label: 'Este año',
    getValue: () => {
      const now = new Date()
      const from = new Date(now.getFullYear(), 0, 1)
      const to = new Date()
      return {
        from: from.toISOString().split('T')[0],
        to: to.toISOString().split('T')[0],
      }
    },
  },
]

export const DateRangePicker: React.FC<DateRangePickerProps> = ({
  value,
  onChange,
  label,
  minDate,
  maxDate = new Date().toISOString().split('T')[0],
  presets = defaultPresets,
  className,
}) => {
  const [showPresets, setShowPresets] = useState(false)

  const handleFromChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({ ...value, from: e.target.value })
  }

  const handleToChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({ ...value, to: e.target.value })
  }

  const handlePresetClick = (preset: typeof presets[0]) => {
    onChange(preset.getValue())
    setShowPresets(false)
  }

  const handleClear = () => {
    onChange({ from: undefined, to: undefined })
  }

  const hasValue = value.from || value.to

  return (
    <div className={cn('space-y-2', className)}>
      {label && (
        <label className="block text-sm font-medium text-gray-700">
          {label}
        </label>
      )}

      <div className="relative">
        {/* Inputs Container */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs text-gray-600 mb-1">Desde</label>
            <div className="relative">
              <Input
                type="date"
                value={value.from || ''}
                onChange={handleFromChange}
                min={minDate}
                max={value.to || maxDate}
                className="pl-9"
              />
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
            </div>
          </div>

          <div>
            <label className="block text-xs text-gray-600 mb-1">Hasta</label>
            <div className="relative">
              <Input
                type="date"
                value={value.to || ''}
                onChange={handleToChange}
                min={value.from || minDate}
                max={maxDate}
                className="pl-9"
              />
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
            </div>
          </div>
        </div>

        {/* Clear Button */}
        {hasValue && (
          <Button
            onClick={handleClear}
            variant="ghost"
            size="sm"
            className="absolute -top-1 right-0 text-gray-400 hover:text-gray-600"
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Presets */}
      {presets.length > 0 && (
        <div>
          <button
            onClick={() => setShowPresets(!showPresets)}
            className="text-xs text-primary-600 hover:text-primary-700 font-medium"
          >
            {showPresets ? 'Ocultar rangos rápidos' : 'Mostrar rangos rápidos'}
          </button>

          {showPresets && (
            <div className="mt-2 grid grid-cols-2 sm:grid-cols-3 gap-2">
              {presets.map((preset, index) => (
                <button
                  key={index}
                  onClick={() => handlePresetClick(preset)}
                  className={cn(
                    'px-3 py-2 text-xs font-medium rounded-lg border transition-colors',
                    'hover:bg-primary-50 hover:border-primary-300',
                    'focus:outline-none focus:ring-2 focus:ring-primary-500',
                    'border-gray-300 text-gray-700'
                  )}
                >
                  {preset.label}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default DateRangePicker
