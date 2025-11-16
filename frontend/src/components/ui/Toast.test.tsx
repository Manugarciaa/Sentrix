import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@/test/utils'
import { ToastProvider, useToast } from './Toast'

// Test component to trigger toasts
function ToastTrigger() {
  const { success, error, warning, info } = useToast()

  return (
    <div>
      <button onClick={() => success('Success!', 'Operation completed')}>Success</button>
      <button onClick={() => error('Error!', 'Something went wrong')}>Error</button>
      <button onClick={() => warning('Warning!', 'Be careful')}>Warning</button>
      <button onClick={() => info('Info', 'Just so you know')}>Info</button>
    </div>
  )
}

describe('Toast', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('displays success toast', async () => {
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>
    )

    const successButton = screen.getByText('Success')
    successButton.click()

    await waitFor(() => {
      expect(screen.getByText('Success!')).toBeInTheDocument()
      expect(screen.getByText('Operation completed')).toBeInTheDocument()
    })
  })

  it('displays error toast', async () => {
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>
    )

    const errorButton = screen.getByText('Error')
    errorButton.click()

    await waitFor(() => {
      expect(screen.getByText('Error!')).toBeInTheDocument()
      expect(screen.getByText('Something went wrong')).toBeInTheDocument()
    })
  })

  it('displays warning toast', async () => {
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>
    )

    const warningButton = screen.getByText('Warning')
    warningButton.click()

    await waitFor(() => {
      expect(screen.getByText('Warning!')).toBeInTheDocument()
      expect(screen.getByText('Be careful')).toBeInTheDocument()
    })
  })

  it('displays info toast', async () => {
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>
    )

    const infoButton = screen.getByText('Info')
    infoButton.click()

    await waitFor(() => {
      expect(screen.getByText('Info')).toBeInTheDocument()
      expect(screen.getByText('Just so you know')).toBeInTheDocument()
    })
  })

  it('removes toast after duration', async () => {
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>
    )

    const successButton = screen.getByText('Success')
    successButton.click()

    await waitFor(() => {
      expect(screen.getByText('Success!')).toBeInTheDocument()
    })

    // Fast forward time
    vi.advanceTimersByTime(5000)

    await waitFor(() => {
      expect(screen.queryByText('Success!')).not.toBeInTheDocument()
    })
  })

  it('can display multiple toasts', async () => {
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>
    )

    screen.getByText('Success').click()
    screen.getByText('Error').click()

    await waitFor(() => {
      expect(screen.getByText('Success!')).toBeInTheDocument()
      expect(screen.getByText('Error!')).toBeInTheDocument()
    })
  })

  it('can close toast manually', async () => {
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>
    )

    const successButton = screen.getByText('Success')
    successButton.click()

    await waitFor(() => {
      expect(screen.getByText('Success!')).toBeInTheDocument()
    })

    const closeButton = screen.getByLabelText(/cerrar notificación/i)
    closeButton.click()

    await waitFor(() => {
      expect(screen.queryByText('Success!')).not.toBeInTheDocument()
    })
  })
})
