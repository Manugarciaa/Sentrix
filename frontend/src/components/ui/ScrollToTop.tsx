/**
 * ScrollToTop Component
 *
 * Scrolls the window to the top whenever the route changes.
 * This ensures that when navigating between pages, users start at the top
 * instead of maintaining the previous scroll position.
 *
 * Usage: Place inside <Router> in App.tsx
 */

import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

export default function ScrollToTop() {
  const { pathname } = useLocation()

  useEffect(() => {
    // Scroll to top when pathname changes
    window.scrollTo({
      top: 0,
      left: 0,
      behavior: 'instant' // Use 'instant' for immediate scroll without animation
    })
  }, [pathname])

  return null // This component doesn't render anything
}
