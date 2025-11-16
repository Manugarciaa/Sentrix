import React from 'react'
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from './Button'

export interface PaginationProps {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
  pageSize?: number
  onPageSizeChange?: (size: number) => void
  pageSizeOptions?: number[]
  className?: string
  showFirstLast?: boolean
  showPageSize?: boolean
}

export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
  pageSize = 10,
  onPageSizeChange,
  pageSizeOptions = [10, 20, 50, 100],
  className,
  showFirstLast = true,
  showPageSize = true,
}) => {
  const getPageNumbers = () => {
    const pages: (number | string)[] = []
    const maxVisible = 7

    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i)
      }
    } else {
      if (currentPage <= 3) {
        for (let i = 1; i <= 5; i++) {
          pages.push(i)
        }
        pages.push('...')
        pages.push(totalPages)
      } else if (currentPage >= totalPages - 2) {
        pages.push(1)
        pages.push('...')
        for (let i = totalPages - 4; i <= totalPages; i++) {
          pages.push(i)
        }
      } else {
        pages.push(1)
        pages.push('...')
        for (let i = currentPage - 1; i <= currentPage + 1; i++) {
          pages.push(i)
        }
        pages.push('...')
        pages.push(totalPages)
      }
    }

    return pages
  }

  const canGoPrevious = currentPage > 1
  const canGoNext = currentPage < totalPages

  return (
    <div className={cn('flex items-center justify-between gap-4 flex-wrap', className)}>
      {/* Page Size Selector */}
      {showPageSize && onPageSizeChange && (
        <div className="flex items-center gap-2">
          <span className="text-sm text-foreground">Mostrar:</span>
          <select
            value={pageSize}
            onChange={(e) => onPageSizeChange(Number(e.target.value))}
            className="h-9 px-3 text-sm bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
          >
            {pageSizeOptions.map((size) => (
              <option key={size} value={size}>
                {size}
              </option>
            ))}
          </select>
          <span className="text-sm text-foreground">por página</span>
        </div>
      )}

      {/* Page Navigation */}
      <div className="flex items-center gap-2">
        {/* First Page */}
        {showFirstLast && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(1)}
            disabled={!canGoPrevious}
            className="h-9 w-9 p-0"
          >
            <ChevronsLeft className="h-4 w-4" />
            <span className="sr-only">Primera página</span>
          </Button>
        )}

        {/* Previous Page */}
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(currentPage - 1)}
          disabled={!canGoPrevious}
          className="h-9 w-9 p-0"
        >
          <ChevronLeft className="h-4 w-4" />
          <span className="sr-only">Página anterior</span>
        </Button>

        {/* Page Numbers */}
        <div className="flex items-center gap-1">
          {getPageNumbers().map((page, index) => {
            if (page === '...') {
              return (
                <span key={`ellipsis-${index}`} className="px-2 text-muted-foreground">
                  ...
                </span>
              )
            }

            const pageNumber = page as number
            const isActive = pageNumber === currentPage

            return (
              <Button
                key={pageNumber}
                variant={isActive ? 'default' : 'outline'}
                size="sm"
                onClick={() => onPageChange(pageNumber)}
                className="h-9 w-9 p-0"
              >
                {pageNumber}
              </Button>
            )
          })}
        </div>

        {/* Next Page */}
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(currentPage + 1)}
          disabled={!canGoNext}
          className="h-9 w-9 p-0"
        >
          <ChevronRight className="h-4 w-4" />
          <span className="sr-only">Página siguiente</span>
        </Button>

        {/* Last Page */}
        {showFirstLast && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(totalPages)}
            disabled={!canGoNext}
            className="h-9 w-9 p-0"
          >
            <ChevronsRight className="h-4 w-4" />
            <span className="sr-only">Última página</span>
          </Button>
        )}
      </div>

      {/* Page Info */}
      <div className="text-sm text-muted-foreground">
        Página {currentPage} de {totalPages}
      </div>
    </div>
  )
}

export default Pagination
