import React from 'react'
import { X, SlidersHorizontal } from 'lucide-react'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/Select'
import { Checkbox } from '@/components/ui/Checkbox'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Label } from '@/components/ui/label'
import { cn } from '@/lib/utils'
import type { AnalysisFilters } from '@/types'

export interface FilterBarProps {
  filters: AnalysisFilters
  onFilterChange: (filters: Partial<AnalysisFilters>) => void
  onReset: () => void
  className?: string
  users?: Array<{ value: string; label: string }>
}

export const FilterBar: React.FC<FilterBarProps> = ({
  filters,
  onFilterChange,
  onReset,
  className,
  users = [],
}) => {
  const [isExpanded, setIsExpanded] = React.useState(false)

  const hasActiveFilters = Boolean(
    filters.risk_level ||
    filters.date_from ||
    filters.date_to ||
    filters.user_id ||
    filters.has_gps ||
    filters.validated_only
  )

  const activeFilterCount = [
    filters.risk_level,
    filters.date_from,
    filters.date_to,
    filters.user_id,
    filters.has_gps,
    filters.validated_only,
  ].filter(Boolean).length

  return (
    <div className={cn('bg-card rounded-xl border border-border shadow-sm', className)}>
      {/* Header */}
      <div className="px-4 py-3 border-b border-border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <SlidersHorizontal className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium text-foreground">Filtros</span>
            {activeFilterCount > 0 && (
              <span className="inline-flex items-center justify-center h-5 w-5 rounded-full text-xs font-medium" style={{
                backgroundColor: 'hsl(var(--primary))',
                color: 'hsl(var(--primary-foreground))'
              }}>
                {activeFilterCount}
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            {hasActiveFilters && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onReset}
                className="text-xs"
              >
                <X className="h-3 w-3 mr-1" />
                Limpiar
              </Button>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
              className="md:hidden"
            >
              {isExpanded ? 'Ocultar' : 'Mostrar'}
            </Button>
          </div>
        </div>
      </div>

      {/* Filters - Horizontal Row Layout */}
      <div className={cn(
        'px-4 py-3 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3',
        !isExpanded && 'hidden md:grid'
      )}>
        {/* Risk Level Filter */}
        <div>
          <label className="block text-xs font-medium text-muted-foreground mb-1.5">
            Nivel de Riesgo
          </label>
          <Select
            value={filters.risk_level ?? 'all'}
            onValueChange={(value) => onFilterChange({ risk_level: value === 'all' ? undefined : value })}
          >
            <SelectTrigger className="h-9">
              <SelectValue placeholder="Todos los niveles" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos los niveles</SelectItem>
              <SelectItem value="ALTO">Alto</SelectItem>
              <SelectItem value="MEDIO">Medio</SelectItem>
              <SelectItem value="BAJO">Bajo</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Date From Filter */}
        <div>
          <label className="block text-xs font-medium text-muted-foreground mb-1.5">
            Desde
          </label>
          <Input
            type="date"
            value={filters.date_from || ''}
            onChange={(e) => onFilterChange({ date_from: e.target.value || undefined })}
            className="h-9 text-sm"
          />
        </div>

        {/* Date To Filter */}
        <div>
          <label className="block text-xs font-medium text-muted-foreground mb-1.5">
            Hasta
          </label>
          <Input
            type="date"
            value={filters.date_to || ''}
            onChange={(e) => onFilterChange({ date_to: e.target.value || undefined })}
            className="h-9 text-sm"
          />
        </div>

        {/* GPS Checkbox */}
        <div>
          <label className="block text-xs font-medium text-muted-foreground mb-1.5">
            Solo con GPS
          </label>
          <div className="flex items-center gap-2 h-9">
            <Checkbox
              id="has_gps"
              checked={filters.has_gps || false}
              onCheckedChange={(checked) => onFilterChange({ has_gps: checked === true ? true : undefined })}
            />
            <Label
              htmlFor="has_gps"
              className="text-sm text-foreground cursor-pointer whitespace-nowrap"
            >
              Activar
            </Label>
          </div>
        </div>

        {/* Validated Only Checkbox */}
        <div>
          <label className="block text-xs font-medium text-muted-foreground mb-1.5">
            Solo validados
          </label>
          <div className="flex items-center gap-2 h-9">
            <Checkbox
              id="validated_only"
              checked={filters.validated_only || false}
              onCheckedChange={(checked) => onFilterChange({ validated_only: checked === true ? true : undefined })}
            />
            <Label
              htmlFor="validated_only"
              className="text-sm text-foreground cursor-pointer whitespace-nowrap"
            >
              Activar
            </Label>
          </div>
        </div>
      </div>
    </div>
  )
}

export default FilterBar
