import { describe, it, expect } from 'vitest'
import { render, screen } from '@/test/utils'
import { Skeleton, SkeletonText, SkeletonCard, SkeletonTable } from './Skeleton'

describe('Skeleton', () => {
  it('renders with default props', () => {
    const { container } = render(<Skeleton />)
    const skeleton = container.firstChild as HTMLElement
    expect(skeleton).toBeInTheDocument()
    expect(skeleton).toHaveClass('bg-gray-200', 'rounded-md', 'animate-pulse')
  })

  it('applies variant classes correctly', () => {
    const { container, rerender } = render(<Skeleton variant="text" />)
    let skeleton = container.firstChild as HTMLElement
    expect(skeleton).toHaveClass('h-4')

    rerender(<Skeleton variant="circular" />)
    skeleton = container.firstChild as HTMLElement
    expect(skeleton).toHaveClass('rounded-full')

    rerender(<Skeleton variant="rectangular" />)
    skeleton = container.firstChild as HTMLElement
    expect(skeleton).toHaveClass('rounded-none')
  })

  it('applies animation correctly', () => {
    const { container, rerender } = render(<Skeleton animation="pulse" />)
    let skeleton = container.firstChild as HTMLElement
    expect(skeleton).toHaveClass('animate-pulse')

    rerender(<Skeleton animation="wave" />)
    skeleton = container.firstChild as HTMLElement
    expect(skeleton).toHaveClass('animate-shimmer')

    rerender(<Skeleton animation="none" />)
    skeleton = container.firstChild as HTMLElement
    expect(skeleton).not.toHaveClass('animate-pulse')
    expect(skeleton).not.toHaveClass('animate-shimmer')
  })

  it('applies custom width and height', () => {
    const { container } = render(<Skeleton width={200} height={100} />)
    const skeleton = container.firstChild as HTMLElement
    expect(skeleton).toHaveStyle({ width: '200px', height: '100px' })
  })
})

describe('SkeletonText', () => {
  it('renders correct number of lines', () => {
    const { container } = render(<SkeletonText lines={5} />)
    const skeletons = container.querySelectorAll('.bg-gray-200')
    expect(skeletons).toHaveLength(5)
  })

  it('makes last line shorter', () => {
    const { container } = render(<SkeletonText lines={3} />)
    const skeletons = container.querySelectorAll('.bg-gray-200')
    const lastSkeleton = skeletons[2]
    expect(lastSkeleton).toHaveClass('w-3/4')
  })
})

describe('SkeletonCard', () => {
  it('renders card skeleton structure', () => {
    const { container } = render(<SkeletonCard />)
    expect(container.querySelector('.border')).toBeInTheDocument()
    expect(container.querySelectorAll('.bg-gray-200').length).toBeGreaterThan(3)
  })
})

describe('SkeletonTable', () => {
  it('renders with default rows and columns', () => {
    const { container } = render(<SkeletonTable />)
    // 5 rows + 1 header = 6 total
    const rows = container.querySelectorAll('.flex.gap-4')
    expect(rows.length).toBeGreaterThanOrEqual(5)
  })

  it('renders custom rows and columns', () => {
    const { container } = render(<SkeletonTable rows={3} columns={5} />)
    const skeletons = container.querySelectorAll('.bg-gray-200')
    // 3 rows + 1 header row = 4 rows * 5 columns = 20 skeletons
    expect(skeletons.length).toBe(20)
  })
})
