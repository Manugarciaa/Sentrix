import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { routes } from '@/lib/config'
import { cn } from '@/lib/utils'

interface PublicLayoutProps {
  children: React.ReactNode
}

const PublicLayout: React.FC<PublicLayoutProps> = ({ children }) => {
  const location = useLocation()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false)
  const [scrolled, setScrolled] = React.useState(false)

  const navigation = [
    { name: 'Inicio', href: routes.public.home },
    { name: 'Reportar', href: routes.public.report },
    { name: 'Acerca de', href: routes.public.about },
    { name: 'Contacto', href: routes.public.contact }
  ]

  const isActive = (href: string) => {
    if (href === routes.public.home) {
      return location.pathname === href
    }
    return location.pathname.startsWith(href)
  }

  React.useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 10)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Navigation */}
      <nav className={cn(
        "top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-200/50 shadow-sm transition-all duration-300",
        scrolled ? "fixed" : "absolute"
      )}>
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-24 justify-between items-center">
            <Link to={routes.public.home} className="flex items-center space-x-3 group">
              <img src="/images/Logo-Sentrix.png" alt="Sentrix" className="h-16 transition-opacity group-hover:opacity-80" />
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex md:items-center md:space-x-8">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className={cn(
                    'text-sm font-semibold transition-colors',
                    isActive(item.href) ? 'text-primary-600' : 'text-gray-800 hover:text-gray-900'
                  )}
                >
                  {item.name}
                </Link>
              ))}
            </div>

            {/* Desktop Auth */}
            <div className="hidden md:flex">
              <Link to={routes.public.login}>
                <Button className="bg-primary-600 hover:bg-primary-700 text-white">Acceder</Button>
              </Link>
            </div>

            {/* Mobile Menu Button */}
            <button
              className="md:hidden p-2 text-gray-900 hover:bg-white/20 rounded-md"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {isMobileMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t bg-white/95 backdrop-blur-md">
            <div className="space-y-1 py-2">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className={cn(
                    'block border-l-4 py-2 pl-3 pr-4 text-base font-medium',
                    isActive(item.href)
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-transparent text-gray-700 hover:bg-gray-50'
                  )}
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  {item.name}
                </Link>
              ))}
            </div>
            <div className="border-t py-3 px-4">
              <Link to={routes.public.login}>
                <Button className="w-full">Acceder</Button>
              </Link>
            </div>
          </div>
        )}
      </nav>

      {/* Content */}
      <main className="flex-1">{children}</main>

      {/* Footer */}
      <footer className="bg-gradient-to-b from-white to-gray-50 border-t border-gray-200">
        <div className="mx-auto max-w-6xl px-4 py-8 sm:py-12 sm:px-6 lg:px-8">
          {/* Logo y descripción */}
          <div className="mb-8 sm:mb-10 text-center sm:text-left">
            <div className="mb-4 flex justify-center sm:justify-start">
              <img src="/images/Logo-Sentrix.png" alt="Sentrix" className="h-12 sm:h-14" />
            </div>
            <p className="text-sm sm:text-base text-gray-600 leading-relaxed max-w-3xl mx-auto sm:mx-0">
              Sistema de detección IA de criaderos de Aedes aegypti mediante visión por computadora.
              Proyecto de tesis UNSTA - Plataforma completa con YOLOv11, geolocalización GPS,
              evaluación de riesgo epidemiológico y gestión inteligente de imágenes para el control del dengue.
            </p>
          </div>

          {/* Enlaces y Contacto */}
          <div className="grid grid-cols-2 gap-6 sm:gap-8 mb-8">
            <div className="text-center sm:text-left">
              <h3 className="text-sm font-bold uppercase tracking-wider text-gray-900 mb-4">
                Enlaces
              </h3>
              <ul className="space-y-2 sm:space-y-3">
                {navigation.map((item) => (
                  <li key={item.name}>
                    <Link
                      to={item.href}
                      className="text-sm text-gray-600 hover:text-primary-600 transition-colors block py-1"
                    >
                      {item.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            <div className="text-center sm:text-left">
              <h3 className="text-sm font-bold uppercase tracking-wider text-gray-900 mb-4">
                Contacto
              </h3>
              <ul className="space-y-2 sm:space-y-3">
                <li className="text-sm text-gray-600 py-1">
                  Tucumán, Argentina
                </li>
                <li className="py-1">
                  <a
                    href="mailto:info@sentrix.com"
                    className="text-sm text-gray-600 hover:text-primary-600 transition-colors"
                  >
                    info@sentrix.com
                  </a>
                </li>
              </ul>
            </div>
          </div>

          {/* Copyright */}
          <div className="pt-6 border-t border-gray-200 text-center">
            <p className="text-sm text-gray-600 flex items-center justify-center gap-2">
              © {new Date().getFullYear()} Sentrix. Todos los derechos reservados.
              <span className="inline-block w-6 h-6">🌱</span>
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default PublicLayout