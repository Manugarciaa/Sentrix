import * as React from 'react'
import { cn } from '@/lib/utils'

interface TabsProps {
  defaultValue?: string
  value?: string
  onValueChange?: (value: string) => void
  className?: string
  children: React.ReactNode
  orientation?: 'horizontal' | 'vertical'
}

interface TabsListProps {
  className?: string
  children: React.ReactNode
}

interface TabsTriggerProps {
  value: string
  className?: string
  children: React.ReactNode
  disabled?: boolean
}

interface TabsContentProps {
  value: string
  className?: string
  children: React.ReactNode
}

const TabsContext = React.createContext<{
  value?: string
  onValueChange?: (value: string) => void
  orientation?: 'horizontal' | 'vertical'
}>({})

const Tabs = React.forwardRef<HTMLDivElement, TabsProps>(
  ({ defaultValue, value, onValueChange, className, children, orientation = 'horizontal', ...props }, ref) => {
    const [selectedValue, setSelectedValue] = React.useState(value || defaultValue || '')

    React.useEffect(() => {
      if (value !== undefined) {
        setSelectedValue(value)
      }
    }, [value])

    const handleValueChange = (newValue: string) => {
      if (value === undefined) {
        setSelectedValue(newValue)
      }
      onValueChange?.(newValue)
    }

    return (
      <TabsContext.Provider
        value={{
          value: selectedValue,
          onValueChange: handleValueChange,
          orientation,
        }}
      >
        <div
          ref={ref}
          className={cn('w-full', className)}
          {...props}
        >
          {children}
        </div>
      </TabsContext.Provider>
    )
  }
)
Tabs.displayName = 'Tabs'

const TabsList = React.forwardRef<HTMLDivElement, TabsListProps>(
  ({ className, children, ...props }, ref) => {
    const { orientation } = React.useContext(TabsContext)

    return (
      <div
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center rounded-md bg-muted p-1 text-muted-foreground',
          orientation === 'vertical' ? 'flex-col h-full' : 'h-10',
          className
        )}
        {...props}
      >
        {children}
      </div>
    )
  }
)
TabsList.displayName = 'TabsList'

const TabsTrigger = React.forwardRef<HTMLButtonElement, TabsTriggerProps>(
  ({ value: triggerValue, className, children, disabled, ...props }, ref) => {
    const { value, onValueChange, orientation } = React.useContext(TabsContext)
    const isSelected = value === triggerValue

    return (
      <button
        ref={ref}
        type="button"
        className={cn(
          'inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
          orientation === 'vertical' ? 'w-full' : '',
          isSelected
            ? 'bg-background text-foreground shadow-sm'
            : 'hover:bg-background/80 hover:text-foreground',
          className
        )}
        onClick={() => !disabled && onValueChange?.(triggerValue)}
        disabled={disabled}
        {...props}
      >
        {children}
      </button>
    )
  }
)
TabsTrigger.displayName = 'TabsTrigger'

const TabsContent = React.forwardRef<HTMLDivElement, TabsContentProps>(
  ({ value: contentValue, className, children, ...props }, ref) => {
    const { value } = React.useContext(TabsContext)
    const isVisible = value === contentValue

    if (!isVisible) return null

    return (
      <div
        ref={ref}
        className={cn(
          'mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
          className
        )}
        {...props}
      >
        {children}
      </div>
    )
  }
)
TabsContent.displayName = 'TabsContent'

export { Tabs, TabsList, TabsTrigger, TabsContent }