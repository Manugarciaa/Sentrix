import React from 'react'
import { cn } from '@/lib/utils'

export interface RadioOption {
  value: string
  label: string
  description?: string
  disabled?: boolean
}

export interface RadioGroupProps {
  label?: string
  options: RadioOption[] | string[]
  value?: string
  onChange?: (value: string) => void
  disabled?: boolean
  className?: string
  error?: string
  orientation?: 'vertical' | 'horizontal'
  name?: string
}

export const RadioGroup: React.FC<RadioGroupProps> = ({
  label,
  options,
  value,
  onChange,
  disabled = false,
  className,
  error,
  orientation = 'vertical',
  name,
}) => {
  const groupName = name || `radio-group-${Math.random().toString(36).substr(2, 9)}`

  const normalizedOptions: RadioOption[] = options.map(option =>
    typeof option === 'string' ? { value: option, label: option } : option
  )

  const handleChange = (optionValue: string) => {
    if (!disabled) {
      onChange?.(optionValue)
    }
  }

  return (
    <div className={cn('w-full', className)}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-3">
          {label}
        </label>
      )}

      <div
        className={cn(
          'flex gap-4',
          orientation === 'vertical' ? 'flex-col' : 'flex-row flex-wrap'
        )}
      >
        {normalizedOptions.map((option) => {
          const optionId = `${groupName}-${option.value}`
          const isSelected = value === option.value
          const isDisabled = disabled || option.disabled

          return (
            <div key={option.value} className="flex items-start">
              <div className="flex items-center h-5">
                <input
                  id={optionId}
                  name={groupName}
                  type="radio"
                  checked={isSelected}
                  onChange={() => handleChange(option.value)}
                  disabled={isDisabled}
                  className="sr-only peer"
                />
                <label
                  htmlFor={optionId}
                  className={cn(
                    'flex items-center justify-center w-5 h-5 border-2 rounded-full cursor-pointer transition-all',
                    'peer-focus-visible:ring-2 peer-focus-visible:ring-primary-500 peer-focus-visible:ring-offset-2',
                    isSelected
                      ? 'border-primary-600'
                      : 'border-gray-300 hover:border-primary-500',
                    isDisabled && 'cursor-not-allowed opacity-60'
                  )}
                >
                  {isSelected && (
                    <div className="w-2.5 h-2.5 bg-primary-600 rounded-full" />
                  )}
                </label>
              </div>

              <div className="ml-3">
                <label
                  htmlFor={optionId}
                  className={cn(
                    'text-sm font-medium cursor-pointer',
                    isDisabled ? 'text-gray-500' : 'text-gray-700'
                  )}
                >
                  {option.label}
                </label>
                {option.description && (
                  <p className="text-sm text-gray-500 mt-0.5">
                    {option.description}
                  </p>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {error && (
        <p className="mt-2 text-sm text-red-600">{error}</p>
      )}
    </div>
  )
}

export const RadioOption: React.FC<{
  value: string
  children: React.ReactNode
}> = () => null // Solo para uso con sintaxis JSX, la lógica está en RadioGroup

export default RadioGroup
