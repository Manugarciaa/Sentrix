import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Home, ArrowLeft, Search } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { routes } from '@/lib/config'

const NotFoundPage: React.FC = () => {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="max-w-md w-full text-center">
        {/* 404 Number */}
        <div className="mb-6">
          <h1
            className="text-8xl font-bold mb-2"
            style={{ color: 'hsl(var(--primary))' }}
          >
            404
          </h1>
          <div className="flex items-center justify-center gap-2 mb-4">
            <Search className="h-5 w-5 text-muted-foreground" />
            <p className="text-lg font-semibold text-foreground">
              Página no encontrada
            </p>
          </div>
        </div>

        {/* Message */}
        <div className="mb-8">
          <p className="text-sm text-muted-foreground mb-2">
            La página que buscas no existe o ha sido movida.
          </p>
          <p className="text-sm text-muted-foreground">
            Verifica la URL o regresa al inicio.
          </p>
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Button
            onClick={() => navigate(-1)}
            variant="outline"
            className="gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Volver
          </Button>
          <Button
            onClick={() => navigate(routes.app.dashboard)}
            className="gap-2"
          >
            <Home className="h-4 w-4" />
            Ir al Inicio
          </Button>
        </div>
      </div>
    </div>
  )
}

export default NotFoundPage
