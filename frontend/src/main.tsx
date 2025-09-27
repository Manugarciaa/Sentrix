import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './globals.css'
import { env } from '@/lib/config'

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

// Enable mock service worker in development
async function enableMocking() {
  if (!env.isDev || !env.enableMocking) {
    return
  }

  try {
    const { worker } = await import('./mocks/browser')
    return worker.start({
      onUnhandledRequest: 'bypass',
    })
  } catch (error) {
    console.warn('Mock service worker not available:', error)
  }
}

// Initialize the app
async function initializeApp() {
  // Enable mocking if needed
  await enableMocking()

  // Initialize authentication state
  const { useAuthStore } = await import('@/store/auth')
  useAuthStore.getState().initializeAuth()

  // Render the app
  ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  )
}

initializeApp().catch(console.error)