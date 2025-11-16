import React from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { routes } from '@/lib/config'
import { useRegister } from '@/hooks/useAuthMutations'
import { AlertCircle, UserPlus } from 'lucide-react'

const RegisterPage: React.FC = () => {
  const registerMutation = useRegister()
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

    registerMutation.mutate({
      email,
      password,
      display_name: name
    })
  }

  return (
    <div className="w-full">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-foreground mb-2">Crear Cuenta</h2>
        <p className="text-muted-foreground">
          Únete a la plataforma de prevención del dengue
        </p>
      </div>

      {/* Error Message */}
      {(registerMutation.error || validationError) && (
        <div className="mb-6 p-4 bg-destructive/10 border border-destructive/30 rounded-lg flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0 mt-0.5" />
          <p className="text-sm text-destructive">
            {validationError || registerMutation.error?.message || 'Error al registrarse'}
          </p>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="space-y-2">
          <label htmlFor="name" className="text-sm font-medium">
            Nombre completo
          </label>
          <Input
            id="name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Tu nombre"
            required
            disabled={registerMutation.isPending}
            className="w-full"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="email" className="text-sm font-medium">
            Email
          </label>
          <Input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="tu@email.com"
            required
            disabled={registerMutation.isPending}
            className="w-full"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="password" className="text-sm font-medium">
            Contraseña
          </label>
          <Input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
            disabled={registerMutation.isPending}
            className="w-full"
          />
          <p className="text-xs text-muted-foreground">Mínimo 8 caracteres</p>
        </div>

        <div className="space-y-2">
          <label htmlFor="confirmPassword" className="text-sm font-medium">
            Confirmar contraseña
          </label>
          <Input
            id="confirmPassword"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="••••••••"
            required
            disabled={registerMutation.isPending}
            className="w-full"
          />
        </div>

        <Button
          type="submit"
          className="w-full gap-2"
          loading={registerMutation.isPending}
          size="lg"
        >
          {!registerMutation.isPending && <UserPlus className="h-4 w-4" />}
          {registerMutation.isPending ? 'Creando cuenta...' : 'Crear Cuenta'}
        </Button>
      </form>

      {/* Footer */}
      <div className="mt-8 space-y-4 text-center">
        <p className="text-sm text-muted-foreground">
          ¿Ya tienes cuenta?{' '}
          <Link to={routes.public.login} className="font-medium text-primary hover:underline">
            Iniciar sesión
          </Link>
        </p>

        <Link
          to={routes.public.home}
          className="inline-block text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          ← Volver al inicio
        </Link>
      </div>
    </div>
  )
}

export default RegisterPage
