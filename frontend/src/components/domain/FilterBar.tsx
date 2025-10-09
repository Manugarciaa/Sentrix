import React from 'react'
import { Search, X, Filter } from 'lucide-react'
import { Select } from '@/components/ui/Select'
import { Checkbox } from '@/components/ui/Checkbox'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { cn } from '@/lib/utils'
import type { AnalysisFilters } from '@/types'

export interface FilterBarProps {
  filters: AnalysisFilters
  onFilterChange: (filters: Partial<AnalysisFilters>) => void
  onReset: () => void
  className?: string
  showSearch?: boolean
  users?: Array<{ value: string; label: string }>
}

export const FilterBar: React.FC<FilterBarProps> = ({
  filters,
  onFilterChange,
  onReset,
  className,
  showSearch = true,
  users = [],
}) => {
  const [searchQuery, setSearchQuery] = React.useState('')
  const [isExpanded, setIsExpanded] = React.useState(false)

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value)
  }

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Implement search logic
    console.log('Search:', searchQuery)
  }

  const hasActiveFilters = Boolean(
    filters.risk_level ||
    filters.date_from ||
    filters.date_to ||
    filters.user_id ||
    filters.has_gps ||
    filters.validated_only
  )

  return (
    <div className={cn('bg-white rounded-xl border border-gray-200 p-4 shadow-sm', className)}>
      {/* Mobile Filter Toggle */}
      <div className="md:hidden mb-4">
        <Button
          variant="outline"
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full justify-between"
        >
          <span className="flex items-center gap-2">
            <Filter className="h-4 w-4" />
            Filtros
            {hasActiveFilters && (
              <span className="inline-flex items-center justify-center h-5 w-5 rounded-full bg-primary-600 text-white text-xs font-medium">
                {Object.values(filters).filter(Boolean).length}
              </span>
            )}
          </span>
          <X className={cn('h-4 w-4 transition-transform', isExpanded ? 'rotate-0' : 'rotate-45')} />
        </Button>
      </div>

      {/* Filters Grid */}
      <div className={cn(
        'grid grid-cols-1 md:grid-cols-4 gap-4',
        !isExpanded && 'hidden md:grid'
      )}>
        {/* Risk Level Filter */}
        <Select
          label="Nivel de Riesgo"
          options={[
            { value: '', label: 'Todos' },
            { value: 'ALTO', label: 'Alto' },
            { value: 'MEDIO', label: 'Medio' },
            { value: 'BAJO', label: 'Bajo' },
          ]}
          value={filters.risk_level || ''}
          onChange={(value) => onFilterChange({ risk_level: value || undefined })}
        />

        {/* Date From Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            Fecha Desde
          </label>
          <Input
            type="date"
            value={filters.date_from || ''}
            onChange={(e) => onFilterChange({ date_from: e.target.value || undefined })}
          />
        </div>

        {/* Date To Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            Fecha Hasta
          </label>
          <Input
            type="date"
            value={filters.date_to || ''}
            onChange={(e) => onFilterChange({ date_to: e.target.value || undefined })}
          />
        </div>

        {/* User Filter */}
        {users.length > 0 && (
          <Select
            label="Usuario"
            options={[{ value: '', label: 'Todos' }, ...users]}
            value={String(filters.user_id || '')}
            onChange={(value) => onFilterChange({ user_id: value ? Number(value) : undefined })}
          />
        )}

        {/* GPS Checkbox */}
        <div className="flex items-end">
          <Checkbox
            label="Solo con GPS"
            checked={filters.has_gps || false}
            onChange={(checked) => onFilterChange({ has_gps: checked || undefined })}
          />
        </div>

        {/* Validated Only Checkbox */}
        <div className="flex items-end">
          <Checkbox
            label="Solo validados"
            checked={filters.validated_only || false}
            onChange={(checked) => onFilterChange({ validated_only: checked || undefined })}
          />
        </div>

        {/* Reset Button */}
        <div className="flex items-end">
          <Button
            variant="outline"
            onClick={onReset}
            disabled={!hasActiveFilters}
            className="w-full"
            size="sm"
          >
            <X className="h-4 w-4 mr-2" />
            Limpiar
          </Button>
        </div>
      </div>

      {/* Search Bar */}
      {showSearch && (
        <form onSubmit={handleSearchSubmit} className="mt-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="search"
              placeholder="Buscar por ID, ubicación..."
              value={searchQuery}
              onChange={handleSearchChange}
              className="pl-10"
            />
          </div>
        </form>
      )}
    </div>
  )
}

export default FilterBar
