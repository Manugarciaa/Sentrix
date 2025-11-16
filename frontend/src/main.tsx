// Polyfill for axios - must be before any imports
interface WindowWithGlobal {
  global?: typeof globalThis
}

if (typeof (window as unknown as WindowWithGlobal).global === 'undefined') {
  (window as unknown as WindowWithGlobal).global = window
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