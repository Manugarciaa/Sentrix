import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { routes } from '@/lib/config'
import { useAuthStore } from '@/store/auth'
import { AlertCircle } from 'lucide-react'
import AuthLayout from '@/components/layouts/AuthLayout'

const RegisterPage: React.FC = () => {
  const navigate = useNavigate()
  const { register, isLoading, error } = useAuthStore()
  const [name, setName] = React.useState('')
  const [email, setEmail] = React.useState('')
  const [password, setPassword] = React.useState('')
  const [confirmPassword, setConfirmPassword] = React.useState('')
  const [validationError, setValidationError] = React.useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setValidationError('')

    if (password !== confirmPassword) {
      setValidationError('Las contraseñas no coinciden')
      return
    }

    if (password.length < 8) {
      setValidationError('La contraseña debe tener al menos 8 caracteres')
      return
    }

    try {
      await register(email, password, name)
      navigate(routes.app.dashboard)
    } catch (err) {
      console.error('Register failed:', err)
    }
  }

  const infoPanel = (
    <>
      <div className="mb-8">
        <h3 className="text-3xl font-bold mb-4">Únete a Sentrix</h3>
        <p className="text-lg text-blue-50 leading-relaxed">
          Forma parte de la red de prevención del dengue y contribuye a
          la salud de tu comunidad con tecnología de punta.
        </p>
      </div>

      <div className="space-y-4">
        <div className="flex items-start gap-3">
          <div className="mt-1">
            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          </div>
          <p className="text-sm text-blue-50">Acceso a herramientas de análisis</p>
        </div>
        <div className="flex items-start gap-3">
          <div className="mt-1">
            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          </div>
          <p className="text-sm text-blue-50">Dashboard personalizado</p>
        </div>
        <div className="flex items-start gap-3">
          <div className="mt-1">
            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          </div>
          <p className="text-sm text-blue-50">Reportes y estadísticas en tiempo real</p>
        </div>
      </div>
    </>
  )

  return (
    <AuthLayout formPosition="right" infoPanel={infoPanel}>
      {/* Form Title */}
      <div className="mb-8 text-center">
        <h2 className="text-2xl font-semibold text-gray-900">Crear Cuenta</h2>
        <p className="text-sm text-gray-600 mt-2">Únete a la plataforma de prevención del dengue</p>
      </div>

      {/* Error Message */}
      {(error || validationError) && (
        <div className="mb-6 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-800">{error || validationError}</p>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1.5">
            Nombre completo
          </label>
          <Input
            id="name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Tu nombre"
            required
            className="w-full"
          />
        </div>

        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1.5">
            Email
          </label>
          <Input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="tu@email.com"
            required
            className="w-full"
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1.5">
            Contraseña
          </label>
          <Input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
            className="w-full"
          />
          <p className="text-xs text-gray-500 mt-1">Mínimo 8 caracteres</p>
        </div>

        <div>
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1.5">
            Confirmar contraseña
          </label>
          <Input
            id="confirmPassword"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="••••••••"
            required
            className="w-full"
          />
        </div>

        <Button type="submit" className="w-full" loading={isLoading} size="lg">
          Crear Cuenta
        </Button>
      </form>

      {/* Login Link */}
      <p className="mt-8 text-center text-sm text-gray-600">
        ¿Ya tienes cuenta?{' '}
        <Link to={routes.public.login} className="font-medium text-primary-600 hover:text-primary-700">
          Iniciar sesión
        </Link>
      </p>

      {/* Back to Home */}
      <div className="mt-6 text-center">
        <Link to={routes.public.home} className="text-sm text-gray-500 hover:text-gray-700">
          ← Volver al inicio
        </Link>
      </div>
    </AuthLayout>
  )
}

export default RegisterPage
