import React from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import AuthLayout from './AuthLayout'
import { useAuthStore } from '@/store/auth'

const AuthLayoutWrapper: React.FC = () => {
  const location = useLocation()
  const isLogin = location.pathname.includes('/login')
  const isLoading = useAuthStore(state => state.isLoading)

  // Panel que se muestra cuando estás en LOGIN (lado derecho visible)
  // Muestra información sobre el sistema
  const loginInfoPanel = (
    <>
      <div className="mb-8">
        <h3 className="text-3xl font-bold mb-4 text-foreground">Prevención del Dengue</h3>
        <p className="text-lg text-muted-foreground leading-relaxed">
          Sistema inteligente para la detección temprana de criaderos de Aedes aegypti
          mediante tecnología de visión artificial.
        </p>
      </div>

      <div className="space-y-4">
        <div className="flex items-start gap-3">
          <div className="mt-1">
            <svg className="h-5 w-5 text-primary" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          </div>
          <p className="text-sm text-muted-foreground">Detección automática con IA</p>
        </div>
        <div className="flex items-start gap-3">
          <div className="mt-1">
            <svg className="h-5 w-5 text-primary" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          </div>
          <p className="text-sm text-muted-foreground">Mapas de riesgo en tiempo real</p>
        </div>
        <div className="flex items-start gap-3">
          <div className="mt-1">
            <svg className="h-5 w-5 text-primary" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          </div>
          <p className="text-sm text-muted-foreground">Análisis y reportes detallados</p>
        </div>
      </div>
    </>
  )

  // Panel que se muestra cuando estás en REGISTER (lado izquierdo visible)
  // Invita a crear cuenta y muestra beneficios
  const registerInfoPanel = (
    <>
      <div className="mb-8">
        <h3 className="text-3xl font-bold mb-4 text-foreground">Únete a Sentrix</h3>
        <p className="text-lg text-muted-foreground leading-relaxed">
          Forma parte de la red de prevención del dengue y contribuye a
          la salud de tu comunidad con tecnología de punta.
        </p>
      </div>

      <div className="space-y-4">
        <div className="flex items-start gap-3">
          <div className="mt-1">
            <svg className="h-5 w-5 text-primary" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          </div>
          <p className="text-sm text-muted-foreground">Acceso a herramientas de análisis</p>
        </div>
        <div className="flex items-start gap-3">
          <div className="mt-1">
            <svg className="h-5 w-5 text-primary" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          </div>
          <p className="text-sm text-muted-foreground">Dashboard personalizado</p>
        </div>
        <div className="flex items-start gap-3">
          <div className="mt-1">
            <svg className="h-5 w-5 text-primary" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          </div>
          <p className="text-sm text-muted-foreground">Reportes y estadísticas en tiempo real</p>
        </div>
      </div>
    </>
  )

  return (
    <AuthLayout
      formPosition={isLogin ? 'left' : 'right'}
      infoPanel={isLogin ? loginInfoPanel : registerInfoPanel}
      loginInfoPanel={loginInfoPanel}
      registerInfoPanel={registerInfoPanel}
      isLoading={isLoading}
      loadingMessage={isLogin ? 'Iniciando sesión...' : 'Creando cuenta...'}
    >
      <Outlet />
    </AuthLayout>
  )
}

export default AuthLayoutWrapper
