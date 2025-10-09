import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { routes } from '@/lib/config'
import { useAuthStore } from '@/store/auth'
import { AlertCircle } from 'lucide-react'

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

  return (
    <>
      {/* Form Title */}
      <div className="mb-8 text-center">
        <h2 className="text-2xl sm:text-3xl font-bold text-gray-800">Crear Cuenta</h2>
        <p className="text-base leading-relaxed text-gray-700 mt-2">Únete a la plataforma de prevención del dengue</p>
      </div>

      {/* Error Message */}
      {(error || validationError) && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-base leading-relaxed text-gray-700">{error || validationError}</p>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label htmlFor="name" className="block text-sm leading-normal text-gray-600 font-medium mb-1.5">
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
          <label htmlFor="email" className="block text-sm leading-normal text-gray-600 font-medium mb-1.5">
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
          <label htmlFor="password" className="block text-sm leading-normal text-gray-600 font-medium mb-1.5">
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
          <p className="text-sm leading-normal text-gray-600 mt-1">Mínimo 8 caracteres</p>
        </div>

        <div>
          <label htmlFor="confirmPassword" className="block text-sm leading-normal text-gray-600 font-medium mb-1.5">
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
      <p className="mt-8 text-center text-base leading-relaxed text-gray-700">
        ¿Ya tienes cuenta?{' '}
        <Link to={routes.public.login} className="font-medium text-primary-600 hover:text-primary-700">
          Iniciar sesión
        </Link>
      </p>

      {/* Back to Home */}
      <div className="mt-6 text-center">
        <Link to={routes.public.home} className="text-sm leading-normal text-gray-600 hover:text-gray-700">
          ← Volver al inicio
        </Link>
      </div>
    </>
  )
}

export default RegisterPage
