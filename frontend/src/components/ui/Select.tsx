import * as React from 'react'
import { cn } from '@/lib/utils'
import { ChevronDown, Check } from 'lucide-react'

interface SelectOption {
  value: string
  label: string
  disabled?: boolean
}

interface SelectProps {
  value?: string
  defaultValue?: string
  onValueChange?: (value: string) => void
  placeholder?: string
  disabled?: boolean
  className?: string
  options: SelectOption[]
  error?: string
  label?: string
}

const Select = React.forwardRef<HTMLButtonElement, SelectProps>(
  ({
    value,
    defaultValue,
    onValueChange,
    placeholder = "Seleccionar...",
    disabled = false,
    className,
    options,
    error,
    label,
    ...props
  }, ref) => {
    const [isOpen, setIsOpen] = React.useState(false)
    const [selectedValue, setSelectedValue] = React.useState(value || defaultValue || '')
    const selectRef = React.useRef<HTMLDivElement>(null)

    React.useEffect(() => {
      if (value !== undefined) {
        setSelectedValue(value)
      }
    }, [value])

    React.useEffect(() => {
      const handleClickOutside = (event: MouseEvent) => {
        if (selectRef.current && !selectRef.current.contains(event.target as Node)) {
          setIsOpen(false)
        }
      }

      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [])

    const handleSelect = (optionValue: string) => {
      setSelectedValue(optionValue)
      onValueChange?.(optionValue)
      setIsOpen(false)
    }

    const selectedOption = options.find(option => option.value === selectedValue)

    return (
      <div className="space-y-2">
        {label && (
          <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
            {label}
          </label>
        )}

        <div className="relative" ref={selectRef}>
          <button
            ref={ref}
            type="button"
            className={cn(
              'flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
              error && 'border-destructive focus:ring-destructive',
              className
            )}
            onClick={() => !disabled && setIsOpen(!isOpen)}
            disabled={disabled}
            {...props}
          >
            <span className={selectedOption ? 'text-foreground' : 'text-muted-foreground'}>
              {selectedOption?.label || placeholder}
            </span>
            <ChevronDown className={cn('h-4 w-4 opacity-50 transition-transform', isOpen && 'rotate-180')} />
          </button>

          {isOpen && (
            <div className="absolute top-full z-50 mt-1 w-full rounded-md border bg-popover shadow-md animate-in fade-in-0 zoom-in-95">
              <div className="p-1 max-h-60 overflow-auto">
                {options.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    className={cn(
                      'relative flex w-full cursor-pointer select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground',
                      option.disabled && 'pointer-events-none opacity-50',
                      selectedValue === option.value && 'bg-accent'
                    )}
                    onClick={() => !option.disabled && handleSelect(option.value)}
                    disabled={option.disabled}
                  >
                    <span className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
                      {selectedValue === option.value && <Check className="h-4 w-4" />}
                    </span>
                    {option.label}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {error && (
          <p className="text-sm text-destructive">
            {error}
          </p>
        )}
      </div>
    )
  }
)
Select.displayName = 'Select'

export { Select, type SelectOption }