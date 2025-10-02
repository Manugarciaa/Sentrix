// Polyfill for axios - must be before any imports
if (typeof (window as any).global === 'undefined') {
  (window as any).global = window
}

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './globals.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)