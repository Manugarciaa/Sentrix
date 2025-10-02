import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './globals.css'
import { env } from '@/lib/config'
import { useAuthStore } from '@/store/auth'

// Initialize PWA
if ('serviceWorker' in navigator && env.isProd) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then(registration => {
        console.log('SW registered: ', registration)
      })
      .catch(registrationError => {
        console.log('SW registration failed: ', registrationError)
      })
  })
}

// Initialize the app
async function initializeApp() {
  // Enable mock service worker ONLY in development
  if (import.meta.env.DEV && env.enableMocking) {
    try {
      const { worker } = await import('./mocks/browser')
      await worker.start({
        onUnhandledRequest: 'bypass',
      })
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