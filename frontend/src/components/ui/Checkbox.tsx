import React from 'react'
import { Check } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface CheckboxProps {
  label?: string
  checked?: boolean
  onChange?: (checked: boolean) => void
  disabled?: boolean
  className?: string
  error?: string
  description?: string
  id?: string
}

export const Checkbox: React.FC<CheckboxProps> = ({
  label,
  checked = false,
  onChange,
  disabled = false,
  className,
  error,
  description,
  id,
}) => {
  const checkboxId = id || `checkbox-${Math.random().toString(36).substr(2, 9)}`

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange?.(e.target.checked)
  }

  return (
    <div className={cn('flex items-start', className)}>
      <div className="flex items-center h-5">
        <input
          id={checkboxId}
          type="checkbox"
          checked={checked}
          onChange={handleChange}
          disabled={disabled}
          className="sr-only peer"
        />
        <label
          htmlFor={checkboxId}
          className={cn(
            'flex items-center justify-center w-5 h-5 border-2 rounded-md cursor-pointer transition-all',
            'peer-focus-visible:ring-2 peer-focus-visible:ring-primary-500 peer-focus-visible:ring-offset-2',
            checked
              ? 'bg-primary-600 border-primary-600'
              : 'bg-white border-gray-300 hover:border-primary-500',
            disabled && 'bg-gray-100 border-gray-300 cursor-not-allowed opacity-60',
            error && 'border-red-500'
          )}
        >
          {checked && <Check className="h-3.5 w-3.5 text-white" strokeWidth={3} />}
        </label>
      </div>

      {(label || description) && (
        <div className="ml-3">
          {label && (
            <label
              htmlFor={checkboxId}
              className={cn(
                'text-sm font-medium cursor-pointer',
                disabled ? 'text-gray-500' : 'text-gray-700'
              )}
            >
              {label}
            </label>
          )}
          {description && (
            <p className="text-sm text-gray-500 mt-0.5">{description}</p>
          )}
          {error && (
            <p className="text-sm text-red-600 mt-0.5">{error}</p>
          )}
        </div>
      )}
    </div>
  )
}

export default Checkbox
