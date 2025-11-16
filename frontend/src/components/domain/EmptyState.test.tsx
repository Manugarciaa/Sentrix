import { describe, it, expect } from 'vitest'
import { render, screen } from '@/test/utils'
import { EmptyState } from './EmptyState'
import { FileText } from 'lucide-react'
import { Button } from '@/components/ui/Button'

describe('EmptyState', () => {
  it('renders title and description', () => {
    render(
      <EmptyState
        icon={FileText}
        title="No results found"
        description="Try adjusting your filters"
      />
    )

    expect(screen.getByText(/no results found/i)).toBeInTheDocument()
    expect(screen.getByText(/try adjusting your filters/i)).toBeInTheDocument()
  })

  it('renders action button', () => {
    render(
      <EmptyState
        icon={FileText}
        title="No results"
        action={<Button>Create new</Button>}
      />
    )

    expect(screen.getByRole('button', { name: /create new/i })).toBeInTheDocument()
  })

  it('renders without description', () => {
    render(<EmptyState icon={FileText} title="Empty" />)

    expect(screen.getByText(/empty/i)).toBeInTheDocument()
    expect(screen.queryByText(/description/i)).not.toBeInTheDocument()
  })

  it('applies variant classes correctly', () => {
    const { container, rerender } = render(
      <EmptyState icon={FileText} title="Test" variant="default" />
    )
    let emptyState = container.firstChild as HTMLElement
    expect(emptyState).not.toHaveClass('bg-gray-50')

    rerender(<EmptyState icon={FileText} title="Test" variant="subtle" />)
    emptyState = container.firstChild as HTMLElement
    expect(emptyState).toHaveClass('bg-gray-50', 'rounded-lg', 'border-gray-200')

    rerender(<EmptyState icon={FileText} title="Test" variant="gradient" />)
    emptyState = container.firstChild as HTMLElement
    expect(emptyState).toHaveClass('bg-gradient-to-br')
  })

  it('renders search illustration', () => {
    const { container } = render(
      <EmptyState icon={FileText} title="Test" illustration="search" />
    )
    const svg = container.querySelector('svg')
    expect(svg).toBeInTheDocument()
    expect(svg?.getAttribute('viewBox')).toBe('0 0 200 200')
  })

  it('renders upload illustration', () => {
    const { container } = render(
      <EmptyState icon={FileText} title="Test" illustration="upload" />
    )
    const svg = container.querySelector('svg')
    expect(svg).toBeInTheDocument()
  })

  it('renders data illustration', () => {
    const { container } = render(
      <EmptyState icon={FileText} title="Test" illustration="data" />
    )
    const svg = container.querySelector('svg')
    expect(svg).toBeInTheDocument()
  })

  it('renders icon when illustration is none', () => {
    const { container } = render(
      <EmptyState icon={FileText} title="Test" illustration="none" />
    )
    // Should find icon in rounded container
    const iconContainer = container.querySelector('.rounded-full')
    expect(iconContainer).toBeInTheDocument()
  })
})
