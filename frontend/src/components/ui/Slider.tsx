import * as React from "react"
import * as SliderPrimitive from "@radix-ui/react-slider"

import { cn } from "@/lib/utils"

interface SliderProps {
  label?: string
  value: number
  onChange: (value: number) => void
  min?: number
  max?: number
  step?: number
  showValue?: boolean
  formatValue?: (value: number) => string
  className?: string
  disabled?: boolean
}

const Slider = React.forwardRef<
  React.ElementRef<typeof SliderPrimitive.Root>,
  SliderProps
>(({
  label,
  value,
  onChange,
  min = 0,
  max = 100,
  step = 1,
  showValue = false,
  formatValue,
  className,
  disabled = false
}, ref) => {
  const handleValueChange = (values: number[]) => {
    onChange(values[0])
  }

  return (
    <div className={cn("space-y-2", className)}>
      {(label || showValue) && (
        <div className="flex items-center justify-between">
          {label && (
            <label className="text-sm font-medium text-foreground">
              {label}
            </label>
          )}
          {showValue && (
            <span className="text-sm font-semibold text-primary">
              {formatValue ? formatValue(value) : value}
            </span>
          )}
        </div>
      )}
      <SliderPrimitive.Root
        ref={ref}
        className={cn(
          "relative flex w-full touch-none select-none items-center",
        )}
        value={[value]}
        onValueChange={handleValueChange}
        min={min}
        max={max}
        step={step}
        disabled={disabled}
      >
        <SliderPrimitive.Track className="relative h-1.5 w-full grow overflow-hidden rounded-full bg-primary/20">
          <SliderPrimitive.Range className="absolute h-full bg-primary" />
        </SliderPrimitive.Track>
        <SliderPrimitive.Thumb className="block h-4 w-4 rounded-full border border-primary/50 bg-background shadow transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50" />
      </SliderPrimitive.Root>
    </div>
  )
})
Slider.displayName = "Slider"

export { Slider }
