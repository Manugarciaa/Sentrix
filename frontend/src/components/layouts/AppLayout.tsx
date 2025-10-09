import React from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/auth'
import { routes } from '@/lib/config'
import { cn } from '@/lib/utils'
import {
  LayoutDashboard,
  Search,
  Upload,
  FileText,
  Users,
  Settings,
  LogOut,
  User,
  Menu,
  X,
  ChevronDown,
} from 'lucide-react'

interface AppLayoutProps {
  children: React.ReactNode
}

interface NavigationItem {
  name: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  roles?: string[]
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const [userMenuOpen, setUserMenuOpen] = React.useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false)

  const navigation: NavigationItem[] = [
    { name: 'Dashboard', href: routes.app.dashboard, icon: LayoutDashboard },
    { name: 'Análisis', href: routes.app.analysis, icon: Search },
    { name: 'Subir', href: routes.app.uploads, icon: Upload },
    { name: 'Reportes', href: routes.app.reports, icon: FileText },
    {
      name: 'Usuarios',
      href: routes.app.users,
      icon: Users,
      roles: ['ADMIN', 'EXPERT']
    },
  ]

  // Filter navigation items based on user role
  const filteredNavigation = navigation.filter(item => {
    if (!item.roles) return true
    return user?.role && item.roles.includes(user.role)
  })

  const isActive = (href: string) => {
    if (href === routes.app.dashboard) {
      return location.pathname === href
    }
    return location.pathname.startsWith(href)
  }

  const handleLogout = () => {
    logout()
    navigate(routes.public.home)
  }

  // Close mobile menu when route changes
  React.useEffect(() => {
    setMobileMenuOpen(false)
  }, [location.pathname])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation - Sticky */}
      <nav className="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            {/* Logo + Mobile Menu Button */}
            <div className="flex items-center gap-4">
              {/* Mobile Menu Button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="lg:hidden p-2 rounded-md text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-colors"
                aria-label="Toggle menu"
              >
                {mobileMenuOpen ? (
                  <X className="h-6 w-6" />
                ) : (
                  <Menu className="h-6 w-6" />
                )}
              </button>

              {/* Logo */}
              <Link to={routes.app.dashboard} className="flex items-center gap-2 group">
                <img
                  src="/images/Logo-Sentrix.png"
                  alt="Sentrix"
                  className="h-10 transition-opacity group-hover:opacity-80"
                />
              </Link>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden lg:flex items-center space-x-1">
              {filteredNavigation.map((item) => {
                const Icon = item.icon
                const active = isActive(item.href)
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={cn(
                      'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all',
                      active
                        ? 'bg-primary-50 text-primary-700 shadow-sm'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{item.name}</span>
                  </Link>
                )
              })}
            </div>

            {/* User Menu */}
            <div className="flex items-center">
              <div className="relative">
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 transition-colors"
                  aria-label="User menu"
                >
                  <div className="h-8 w-8 rounded-full bg-gradient-to-br from-primary-600 to-cyan-600 flex items-center justify-center shadow-sm">
                    <User className="h-4 w-4 text-white" />
                  </div>
                  <div className="hidden md:block text-left">
                    <p className="text-sm font-medium text-gray-900">{user?.name || 'Usuario'}</p>
                    <p className="text-xs text-gray-500">{user?.email || ''}</p>
                  </div>
                  <ChevronDown className={cn(
                    "hidden md:block h-4 w-4 text-gray-400 transition-transform",
                    userMenuOpen && "rotate-180"
                  )} />
                </button>

                {/* User Dropdown Menu */}
                {userMenuOpen && (
                  <>
                    <div
                      className="fixed inset-0 z-40"
                      onClick={() => setUserMenuOpen(false)}
                      onKeyDown={(e) => e.key === 'Escape' && setUserMenuOpen(false)}
                      role="button"
                      tabIndex={0}
                      aria-label="Close menu"
                    />
                    <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-xl border border-gray-200 z-50 overflow-hidden">
                      {/* User Info Header */}
                      <div className="px-4 py-3 bg-gradient-to-br from-primary-50 to-cyan-50 border-b border-gray-200">
                        <p className="text-sm font-semibold text-gray-900">{user?.name || 'Usuario'}</p>
                        <p className="text-xs text-gray-600 truncate">{user?.email || ''}</p>
                        {user?.role && (
                          <span className={cn(
                            "inline-block mt-1.5 px-2 py-0.5 text-xs font-medium rounded-full",
                            user.role === 'ADMIN' && "bg-purple-100 text-purple-700",
                            user.role === 'EXPERT' && "bg-blue-100 text-blue-700",
                            user.role === 'USER' && "bg-gray-100 text-gray-700"
                          )}>
                            {user.role}
                          </span>
                        )}
                      </div>

                      {/* Menu Items */}
                      <div className="p-2">
                        <Link
                          to={routes.app.profile}
                          className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
                          onClick={() => setUserMenuOpen(false)}
                        >
                          <User className="h-4 w-4" />
                          <span>Mi Perfil</span>
                        </Link>
                        <Link
                          to={routes.app.settings}
                          className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
                          onClick={() => setUserMenuOpen(false)}
                        >
                          <Settings className="h-4 w-4" />
                          <span>Configuración</span>
                        </Link>
                        <div className="border-t border-gray-100 my-1" />
                        <button
                          onClick={handleLogout}
                          className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        >
                          <LogOut className="h-4 w-4" />
                          <span>Cerrar Sesión</span>
                        </button>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        {mobileMenuOpen && (
          <div className="lg:hidden border-t border-gray-200 bg-white shadow-lg">
            <div className="px-4 py-3 space-y-1">
              {filteredNavigation.map((item) => {
                const Icon = item.icon
                const active = isActive(item.href)
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={cn(
                      'flex items-center gap-3 px-4 py-3 rounded-lg text-base font-medium transition-colors',
                      active
                        ? 'bg-primary-50 text-primary-700 border-l-4 border-primary-600'
                        : 'text-gray-700 hover:bg-gray-50 border-l-4 border-transparent'
                    )}
                  >
                    <Icon className="h-5 w-5" />
                    <span>{item.name}</span>
                  </Link>
                )
              })}
            </div>
          </div>
        )}
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  )
}

export default AppLayout
