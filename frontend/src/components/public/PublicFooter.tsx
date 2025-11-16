import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Mail, MapPin } from 'lucide-react'
import { Logo } from '@/components/ui/Logo'
import { routes } from '@/lib/config'

const PublicFooter: React.FC = () => {
  const currentYear = new Date().getFullYear()
  const location = useLocation()
  const isHomePage = location.pathname === routes.public.home

  // Navegación para HomePage (scroll a secciones)
  const homeLinks = [
    { name: 'Inicio', href: '#hero' },
    { name: 'Información', href: '#dengue' },
    { name: 'Demo IA', href: '#demo' },
    { name: 'Mapa', href: '#mapa' }
  ]

  // Navegación para otras páginas
  const otherLinks = [
    { name: 'Inicio', href: routes.public.home }
  ]

  const links = isHomePage ? homeLinks : otherLinks

  const handleScrollClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    if (isHomePage && href.startsWith('#')) {
      e.preventDefault()
      const elementId = href.replace('#', '')
      const element = document.getElementById(elementId)
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' })
      } else if (href === '#hero') {
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    }
  }

  return (
    <footer className="relative bg-background border-t border-border">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-16">
        {/* Main Footer Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12 mb-12">
          {/* Logo y descripción */}
          <div>
            <Logo className="h-10 mb-4" />
            <p className="text-sm text-muted-foreground leading-relaxed">
              Sistema de detección inteligente de criaderos de <em>Aedes aegypti</em> para la prevención del dengue.
            </p>
          </div>

          {/* Navegación */}
          <div>
            <h3 className="text-sm font-semibold text-foreground mb-4">Navegación</h3>
            <ul className="space-y-2">
              {links.map((link) => (
                <li key={link.name}>
                  <a
                    href={link.href}
                    onClick={(e) => handleScrollClick(e, link.href)}
                    className="text-sm text-muted-foreground hover:text-primary transition-colors"
                  >
                    {link.name}
                  </a>
                </li>
              ))}
              <li>
                <Link
                  to={routes.public.login}
                  className="text-sm text-muted-foreground hover:text-primary transition-colors"
                >
                  Acceder
                </Link>
              </li>
            </ul>
          </div>

          {/* Contacto */}
          <div>
            <h3 className="text-sm font-semibold text-foreground mb-4">Contacto</h3>
            <ul className="space-y-3">
              <li className="flex items-start gap-2">
                <MapPin className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-sm text-muted-foreground">Tucumán, Argentina</span>
              </li>
              <li className="flex items-start gap-2">
                <Mail className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                <a
                  href="mailto:contact@sentrix.ar"
                  className="text-sm text-muted-foreground hover:text-primary transition-colors"
                >
                  contact@sentrix.ar
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-border">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-muted-foreground">
            <p className="text-center md:text-left">
              © {currentYear} Sentrix. Proyecto académico de tesis.
            </p>
            <p className="text-center md:text-right">
              Universidad del Norte Santo Tomás de Aquino (UNSTA)
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default PublicFooter
