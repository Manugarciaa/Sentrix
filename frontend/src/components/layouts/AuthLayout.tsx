import React from 'react'
import { useMediaQuery } from '@/hooks/useMediaQuery'
import { Loader2 } from 'lucide-react'

interface AuthLayoutProps {
  children: React.ReactNode
  infoPanel: React.ReactNode
  formPosition?: 'left' | 'right'
  loginInfoPanel?: React.ReactNode
  registerInfoPanel?: React.ReactNode
  isLoading?: boolean
  loadingMessage?: string
}

const AuthLayout: React.FC<AuthLayoutProps> = ({
  children,
  infoPanel,
  formPosition = 'left',
  loginInfoPanel,
  registerInfoPanel,
  isLoading = false,
  loadingMessage = 'Procesando...'
}) => {
  const isLogin = formPosition === 'left'
  const isDesktop = useMediaQuery('(min-width: 1024px)')

  // Use specific panels if provided, otherwise fall back to generic infoPanel
  const loginInfo = loginInfoPanel || infoPanel
  const registerInfo = registerInfoPanel || infoPanel

  return (
    <div className="min-h-screen bg-background relative">
      {!isDesktop ? (
        /* Mobile Layout - Only form */
        <div className="flex min-h-screen">
          <div className="flex-1 flex items-center justify-center bg-background px-6 py-12">
            <div className="w-full max-w-md">
              {children}
            </div>
          </div>
        </div>
      ) : (
        /* Desktop Layout - Swap animation with 4 independent elements */
        <div className="relative min-h-screen overflow-hidden">
          {/* Login Form - Left side, slides out to the right when switching to register */}
          <div
            className="absolute inset-y-0 left-0 w-1/2 flex items-center justify-center bg-background p-8 transition-all duration-700 ease-in-out overflow-hidden"
            style={{
              transform: isLogin ? 'translateX(0%)' : 'translateX(100%)',
              opacity: isLogin ? 1 : 0,
              zIndex: isLogin ? 10 : 0
            }}
          >
            {isLogin && (
              <div className="w-full max-w-md relative">
                {children}

                {/* Loading overlay for login form */}
                {isLoading && (
                  <div className="absolute inset-0 flex items-center justify-center bg-background/70 backdrop-blur-[2px] rounded-lg">
                    <div className="flex flex-col items-center gap-3">
                      <Loader2 className="h-10 w-10 text-primary animate-spin" />
                      <p className="text-sm font-medium text-foreground">{loadingMessage}</p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Login Info Panel - Right side, slides out to the right when switching to register */}
          <div
            className="absolute inset-y-0 right-0 w-1/2 flex items-center justify-center p-12 transition-all duration-700 ease-in-out overflow-hidden bg-primary/10 dark:bg-primary/20"
            style={{
              transform: isLogin ? 'translateX(0%)' : 'translateX(100%)',
              opacity: isLogin ? 1 : 0,
              zIndex: isLogin ? 10 : 0
            }}
          >
            <div className="relative z-10 max-w-md w-full">
              {loginInfo}
            </div>
          </div>

          {/* Register Info Panel - Slides in from the left when switching to register */}
          <div
            className="absolute inset-y-0 left-0 w-1/2 flex items-center justify-center p-12 transition-all duration-700 ease-in-out overflow-hidden bg-primary/10 dark:bg-primary/20"
            style={{
              transform: isLogin ? 'translateX(100%)' : 'translateX(0%)',
              opacity: isLogin ? 0 : 1,
              zIndex: isLogin ? 0 : 10
            }}
          >
            <div className="relative z-10 max-w-md w-full">
              {registerInfo}
            </div>
          </div>

          {/* Register Form - Slides in from the left when switching to register */}
          <div
            className="absolute inset-y-0 right-0 w-1/2 flex items-center justify-center bg-background p-8 transition-all duration-700 ease-in-out overflow-hidden"
            style={{
              transform: isLogin ? 'translateX(100%)' : 'translateX(0%)',
              opacity: isLogin ? 0 : 1,
              zIndex: isLogin ? 0 : 10
            }}
          >
            {!isLogin && (
              <div className="w-full max-w-md relative">
                {children}

                {/* Loading overlay for register form */}
                {isLoading && (
                  <div className="absolute inset-0 flex items-center justify-center bg-background/70 backdrop-blur-[2px] rounded-lg">
                    <div className="flex flex-col items-center gap-3">
                      <Loader2 className="h-10 w-10 text-primary animate-spin" />
                      <p className="text-sm font-medium text-foreground">{loadingMessage}</p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default AuthLayout
