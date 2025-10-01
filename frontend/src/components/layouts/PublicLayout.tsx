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

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Navigation */}
      <nav className="border-b border-gray-100 bg-white sticky top-0 z-50">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 justify-between items-center">
            <Link to={routes.public.home} className="flex items-center space-x-3 group">
              <div className="h-9 w-9 rounded-xl bg-primary-600 flex items-center justify-center group-hover:bg-primary-700 transition-colors">
                <svg className="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <span className="text-xl font-bold text-gray-800 group-hover:text-primary-700 transition-colors">Sentrix</span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex md:items-center md:space-x-8">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className={cn(
                    'text-sm font-medium transition-colors',
                    isActive(item.href) ? 'text-primary-600 font-semibold' : 'text-gray-600 hover:text-gray-800'
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
              className="md:hidden p-2 text-gray-400 hover:bg-gray-100 rounded-md"
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
          <div className="md:hidden border-t">
            <div className="space-y-1 py-2">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className={cn(
                    'block border-l-4 py-2 pl-3 pr-4 text-base font-medium',
                    isActive(item.href)
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-transparent text-gray-500 hover:bg-gray-50'
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
      <footer className="bg-white border-t border-gray-100">
        <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-3">
                <div className="h-8 w-8 rounded-lg bg-primary-600 flex items-center justify-center">
                  <svg className="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <span className="text-xl font-bold text-gray-800">Sentrix</span>
              </div>
              <p className="text-sm text-gray-600">
                Detección de criaderos de Aedes aegypti con IA
              </p>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-gray-800 uppercase mb-3">Enlaces</h3>
              <ul className="space-y-2">
                {navigation.map((item) => (
                  <li key={item.name}>
                    <Link to={item.href} className="text-sm text-gray-600 hover:text-gray-800">
                      {item.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-gray-800 uppercase mb-3">Contacto</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>Tucumán, Argentina</li>
                <li><a href="mailto:info@sentrix.com.ar" className="hover:text-gray-800">info@sentrix.com.ar</a></li>
              </ul>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-gray-100 text-center">
            <p className="text-sm text-gray-500">
              © {new Date().getFullYear()} Sentrix. Todos los derechos reservados.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default PublicLayout