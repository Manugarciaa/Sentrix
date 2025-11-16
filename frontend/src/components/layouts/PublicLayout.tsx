import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { ThemeToggle } from '@/components/ui/ThemeToggle'
import { Logo } from '@/components/ui/Logo'
import PublicFooter from '@/components/public/PublicFooter'
import { routes } from '@/lib/config'
import { cn } from '@/lib/utils'
import { Menu, X } from 'lucide-react'

interface PublicLayoutProps {
  children: React.ReactNode
}

const PublicLayout: React.FC<PublicLayoutProps> = ({ children }) => {
  const location = useLocation()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false)
  const [scrolled, setScrolled] = React.useState(false)

  const isHomePage = location.pathname === routes.public.home

  // Navegación para HomePage (scroll a secciones)
  const homeNavigation = [
    { name: 'Inicio', href: '#hero', scroll: true },
    { name: 'Información', href: '#dengue', scroll: true },
    { name: 'Demo IA', href: '#demo', scroll: true },
    { name: 'Mapa', href: '#mapa', scroll: true }
  ]

  // Navegación para otras páginas
  const otherNavigation = [
    { name: 'Inicio', href: routes.public.home }
  ]

  const navigation = isHomePage ? homeNavigation : otherNavigation

  const handleNavClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string, scroll?: boolean) => {
    if (scroll && isHomePage) {
      e.preventDefault()

      // Cerrar menú móvil INMEDIATAMENTE para que el cálculo de scroll sea correcto
      setIsMobileMenuOpen(false)

      const elementId = href.replace('#', '')

      // Para "Inicio" (#hero), ir siempre al top sin offset
      if (href === '#hero') {
        // Pequeño delay para que el menú móvil se cierre antes de scrollear
        setTimeout(() => {
          window.scrollTo({ top: 0, behavior: 'smooth' })
        }, 50)
        return
      }

      const element = document.getElementById(elementId)

      if (element) {
        // Pequeño delay para que el menú móvil se cierre completamente antes de scrollear
        setTimeout(() => {
          // El scroll-mt-16 en los títulos ya contempla el offset del navbar
          element.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }, 50)
      }
    }
  }

  const isActive = (href: string) => {
    if (href.startsWith('#')) {
      return false // Active state for scroll links handled differently
    }
    if (href === routes.public.home) {
      return location.pathname === href
    }
    return location.pathname.startsWith(href)
  }

  React.useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Close mobile menu on route change
  React.useEffect(() => {
    setIsMobileMenuOpen(false)
  }, [location.pathname])

  return (
    <div className="min-h-screen bg-background flex flex-col transition-colors duration-300">
      {/* Navigation - Sticky Header más compacto */}
      <nav className={cn(
        "sticky top-0 left-0 right-0 z-50 transition-all duration-300",
        "bg-background/95 dark:bg-background/90 backdrop-blur-md",
        "border-b border-border/50",
        scrolled && "shadow-md"
      )}>
        <div className="sentrix-container">
          <div className="flex h-16 justify-between items-center">
            {/* Logo */}
            <Link to={routes.public.home} className="flex items-center group">
              <Logo className="h-10 group-hover:opacity-80 transition-opacity" />
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex md:items-center md:space-x-1">
              {navigation.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  onClick={(e) => handleNavClick(e, item.href, 'scroll' in item ? item.scroll : false)}
                  className={cn(
                    'px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200',
                    isActive(item.href)
                      ? 'bg-primary/10 text-primary'
                      : 'text-foreground hover:bg-muted'
                  )}
                >
                  {item.name}
                </a>
              ))}
            </div>

            {/* Desktop Auth + Theme Toggle */}
            <div className="hidden md:flex items-center gap-2">
              <ThemeToggle />
              <Link to={routes.public.login}>
                <Button
                  size="sm"
                  className="bg-primary hover:bg-primary/90 dark:hover:bg-primary/80 text-white shadow-sm"
                >
                  Acceder
                </Button>
              </Link>
            </div>

            {/* Mobile Menu Button */}
            <button
              className="md:hidden p-2 text-foreground hover:bg-muted rounded-lg transition-colors"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              aria-label="Toggle menu"
            >
              {isMobileMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t border-border bg-background/95 backdrop-blur-md">
            <div className="sentrix-container py-4 space-y-1">
              {navigation.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  onClick={(e) => handleNavClick(e, item.href, 'scroll' in item ? item.scroll : false)}
                  className={cn(
                    'block border-l-4 py-3 pl-4 pr-4 text-base font-medium rounded-r-lg transition-all',
                    isActive(item.href)
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-transparent text-foreground hover:bg-muted hover:border-primary/30'
                  )}
                >
                  {item.name}
                </a>
              ))}
              <div className="border-t border-border pt-4 mt-4 flex items-center gap-3">
                <ThemeToggle className="flex-shrink-0" />
                <Link to={routes.public.login} className="flex-1" onClick={() => setIsMobileMenuOpen(false)}>
                  <Button className="w-full bg-primary hover:bg-primary/90 dark:hover:bg-primary/80 text-white">
                    Acceder
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        )}
      </nav>

      {/* Content */}
      <main className="flex-1">{children}</main>

      {/* Footer */}
      <PublicFooter />
    </div>
  )
}

export default PublicLayout