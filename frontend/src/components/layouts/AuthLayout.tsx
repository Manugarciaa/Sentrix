import React, { useEffect, useState } from 'react'

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
  const [isTransitioning, setIsTransitioning] = useState(false)
  const [mounted, setMounted] = useState(false)
  const previousPosition = React.useRef(formPosition)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted) return

    if (previousPosition.current !== formPosition) {
      setIsTransitioning(true)
      const timer = setTimeout(() => setIsTransitioning(false), 400)
      previousPosition.current = formPosition
      return () => clearTimeout(timer)
    }
  }, [formPosition, mounted])

  const isFormLeft = formPosition === 'left'

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      <div className="w-full h-screen">
        <div className="grid lg:grid-cols-2 gap-0 h-full">
          {/* Form Panel */}
          <div
            className={`${
              isFormLeft ? 'lg:order-1' : 'lg:order-2'
            } flex items-center justify-center p-8 lg:p-12 bg-white/80 backdrop-blur-sm transition-opacity duration-500 ease-out ${
              isTransitioning ? 'opacity-0' : 'opacity-100'
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
            } hidden lg:flex items-center justify-center bg-gradient-to-br from-sky-100 via-blue-100 to-cyan-100 p-12 transition-opacity duration-500 ease-out relative overflow-hidden`}
          >
            {/* Decorative background patterns */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_30%,rgba(14,165,233,0.3)_0%,transparent_60%)]"></div>
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_70%,rgba(6,182,212,0.25)_0%,transparent_60%)]"></div>

            <div className={`max-w-md relative z-10 transition-opacity duration-500 ease-out ${
              isTransitioning ? 'opacity-0' : 'opacity-100'
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
