import React, { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

interface AuthLayoutProps {
  children: React.ReactNode
  infoPanel: React.ReactNode
  formPosition?: 'left' | 'right'
}

const AuthLayout: React.FC<AuthLayoutProps> = ({
  children,
  infoPanel,
  formPosition = 'left'
}) => {
  const location = useLocation()
  const [isTransitioning, setIsTransitioning] = useState(false)

  useEffect(() => {
    setIsTransitioning(true)
    const timer = setTimeout(() => setIsTransitioning(false), 500)
    return () => clearTimeout(timer)
  }, [location.pathname])

  const isFormLeft = formPosition === 'left'

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="w-full h-screen">
        <div className="grid lg:grid-cols-2 gap-0 bg-white h-full">
          {/* Form Panel */}
          <div
            className={`${
              isFormLeft ? 'lg:order-1' : 'lg:order-2'
            } flex items-center justify-center p-8 lg:p-12 transition-all duration-500 ease-in-out ${
              isTransitioning ? 'opacity-0 scale-95' : 'opacity-100 scale-100'
            }`}
          >
            <div className="w-full max-w-md">
              {children}
            </div>
          </div>

          {/* Info Panel */}
          <div
            className={`${
              isFormLeft ? 'lg:order-2' : 'lg:order-1'
            } hidden lg:flex items-center justify-center bg-gradient-to-br from-primary-600 via-primary-500 to-cyan-600 p-12 transition-all duration-500 ease-in-out relative overflow-hidden ${
              isTransitioning ? 'opacity-90' : 'opacity-100'
            }`}
          >
            <div className={`max-w-md text-white relative z-10 transition-all duration-500 ${
              isTransitioning ? 'opacity-0 translate-x-8' : 'opacity-100 translate-x-0'
            }`}>
              {infoPanel}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AuthLayout
