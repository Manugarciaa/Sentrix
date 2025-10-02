import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './globals.css'
import { useAuthStore } from '@/store/auth'

// Initialize the app
async function initializeApp() {
  // Enable mock service worker ONLY in development
  if (import.meta.env.DEV) {
    try {
      const enableMocking = import.meta.env.VITE_ENABLE_MOCKING === 'true'
      if (enableMocking) {
        const { worker } = await import('./mocks/browser')
        await worker.start({
          onUnhandledRequest: 'bypass',
        })
        console.log('Mock service worker started')
      }
    } catch (error) {
      console.warn('Mock service worker not available:', error)
    }
  }

  // Initialize authentication state
  useAuthStore.getState().initializeAuth()

  // Render the app
  ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  )
}

initializeApp().catch(console.error)