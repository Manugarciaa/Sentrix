import { describe, it, expect } from 'vitest'
import { render, screen } from '@/test/utils'
import { Card } from './Card'

describe('Card', () => {
  it('renders children correctly', () => {
    render(
      <Card>
        <div>Card Content</div>
      </Card>
    )
    expect(screen.getByText(/card content/i)).toBeInTheDocument()
  })

  it('applies variant classes correctly', () => {
    const { rerender, container } = render(<Card variant="default">Content</Card>)
    let card = container.firstChild as HTMLElement
    expect(card).toHaveClass('bg-white', 'border-gray-200')

    rerender(<Card variant="gradient">Content</Card>)
    card = container.firstChild as HTMLElement
    expect(card).toHaveClass('bg-gradient-to-br')
  })

  it('applies hover effect when hoverable', () => {
    const { container } = render(<Card hoverable>Content</Card>)
    const card = container.firstChild as HTMLElement
    expect(card).toHaveClass('hover:shadow-lg', 'transition-shadow')
  })

  it('applies custom className', () => {
    const { container } = render(<Card className="custom-class">Content</Card>)
    const card = container.firstChild as HTMLElement
    expect(card).toHaveClass('custom-class')
  })

  it('forwards ref correctly', () => {
    const ref = { current: null }
    render(<Card ref={ref as any}>Content</Card>)
    expect(ref.current).toBeInstanceOf(HTMLDivElement)
  })
})
