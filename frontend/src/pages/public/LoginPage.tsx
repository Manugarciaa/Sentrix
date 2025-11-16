import React from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { routes } from '@/lib/config'
import { useLogin } from '@/hooks/useAuthMutations'
import { AlertCircle, LogIn } from 'lucide-react'

const LoginPage: React.FC = () => {
  const loginMutation = useLogin()
  const [email, setEmail] = React.useState('')
  const [password, setPassword] = React.useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    loginMutation.mutate({ email, password })
  }

  return (
    <div className="w-full">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-foreground mb-2">Iniciar Sesión</h2>
        <p className="text-muted-foreground">
          Ingresa tus credenciales para continuar
        </p>
      </div>

      {/* Error Message */}
      {loginMutation.isError && loginMutation.error && (
        <div className="mb-6 p-4 bg-destructive/10 border border-destructive/30 rounded-lg flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0 mt-0.5" />
          <p className="text-sm text-destructive">
            {typeof loginMutation.error === 'string'
              ? loginMutation.error
              : (loginMutation.error as any)?.message || 'Error al iniciar sesión'}
          </p>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-5">
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
            disabled={loginMutation.isPending}
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
            disabled={loginMutation.isPending}
            className="w-full"
          />
        </div>

        <Button
          type="submit"
          className="w-full gap-2"
          loading={loginMutation.isPending}
          size="lg"
        >
          {!loginMutation.isPending && <LogIn className="h-4 w-4" />}
          {loginMutation.isPending ? 'Iniciando sesión...' : 'Iniciar Sesión'}
        </Button>
      </form>

      {/* Footer */}
      <div className="mt-8 space-y-4 text-center">
        <p className="text-sm text-muted-foreground">
          ¿No tienes cuenta?{' '}
          <Link to={routes.public.register} className="font-medium text-primary hover:underline">
            Crear cuenta
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

export default LoginPage
