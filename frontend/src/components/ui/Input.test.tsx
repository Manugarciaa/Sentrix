import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@/test/utils'
import userEvent from '@testing-library/user-event'
import { Input } from './Input'
import { Mail } from 'lucide-react'

describe('Input', () => {
  it('renders with label', () => {
    render(<Input label="Email" />)
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
  })

  it('handles input changes', async () => {
    const handleChange = vi.fn()
    const user = userEvent.setup()

    render(<Input label="Email" onChange={handleChange} />)
    const input = screen.getByLabelText(/email/i)

    await user.type(input, 'test@example.com')
    expect(handleChange).toHaveBeenCalled()
    expect(input).toHaveValue('test@example.com')
  })

  it('displays error message', () => {
    render(<Input label="Email" error="Email is required" />)
    expect(screen.getByText(/email is required/i)).toBeInTheDocument()
    const input = screen.getByLabelText(/email/i)
    expect(input).toHaveClass('border-red-500')
  })

  it('shows required indicator', () => {
    render(<Input label="Email" required />)
    expect(screen.getByText('*')).toBeInTheDocument()
  })

  it('renders with icon', () => {
    render(<Input label="Email" icon={Mail} />)
    const input = screen.getByLabelText(/email/i)
    expect(input.parentElement?.querySelector('svg')).toBeInTheDocument()
  })

  it('can be disabled', () => {
    render(<Input label="Email" disabled />)
    const input = screen.getByLabelText(/email/i)
    expect(input).toBeDisabled()
  })

  it('supports different types', () => {
    const { rerender } = render(<Input label="Password" type="password" />)
    let input = screen.getByLabelText(/password/i)
    expect(input).toHaveAttribute('type', 'password')

    rerender(<Input label="Number" type="number" />)
    input = screen.getByLabelText(/number/i)
    expect(input).toHaveAttribute('type', 'number')
  })

  it('displays helper text', () => {
    render(<Input label="Email" helperText="We'll never share your email" />)
    expect(screen.getByText(/we'll never share your email/i)).toBeInTheDocument()
  })
})
