import React from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/auth'
import { useAppStore, useSidebarOpen } from '@/store/app'
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
  Menu,
  X,
  ChevronDown,
  User,
  Bell,
} from 'lucide-react'

interface AppLayoutProps {
  children: React.ReactNode
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const { setSidebarOpen, toggleSidebar } = useAppStore()
  const sidebarOpen = useSidebarOpen()
  const [userMenuOpen, setUserMenuOpen] = React.useState(false)

  const navigation = [
    { name: 'Dashboard', href: routes.app.dashboard, icon: LayoutDashboard },
    { name: 'Análisis', href: routes.app.analysis, icon: Search },
    { name: 'Subir Imágenes', href: routes.app.uploads, icon: Upload },
    { name: 'Reportes', href: routes.app.reports, icon: FileText },
    { name: 'Usuarios', href: routes.app.users, icon: Users },
    { name: 'Configuración', href: routes.app.settings, icon: Settings },
  ]

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

  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element
      if (!target.closest('[data-user-menu]')) {
        setUserMenuOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div className="h-screen flex overflow-hidden" style={{ backgroundColor: '#F5F5F5' }}>
      {/* Sidebar */}
      <div
        className={cn(
          'relative flex-shrink-0 transition-all duration-300 ease-in-out',
          sidebarOpen ? 'w-64' : 'w-16'
        )}
      >
        {/* Sidebar backdrop for mobile */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Sidebar content */}
        <div
          className={cn(
            'relative flex flex-col w-64 h-full bg-white border-r border-gray-200 transition-transform duration-300 ease-in-out z-50',
            'lg:translate-x-0',
            sidebarOpen ? 'translate-x-0' : '-translate-x-48 lg:w-16'
          )}
        >
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200">
            <div className="flex items-center space-x-2">
              <div className="h-8 w-8 rounded-lg bg-primary-600 flex items-center justify-center">
                <svg
                  className="h-5 w-5 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              {sidebarOpen && (
                <span className="text-xl font-bold text-gray-900">Sentrix</span>
              )}
            </div>
            <button
              type="button"
              className="p-1.5 rounded-md text-gray-400 hover:bg-gray-100 hover:text-gray-500 lg:hidden"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
              const Icon = item.icon
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={cn(
                    'group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors',
                    isActive(item.href)
                      ? 'bg-primary-100 text-primary-900'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  )}
                  title={!sidebarOpen ? item.name : ''}
                >
                  <Icon
                    className={cn(
                      'flex-shrink-0 h-5 w-5 transition-colors',
                      isActive(item.href)
                        ? 'text-primary-500'
                        : 'text-gray-400 group-hover:text-gray-500'
                    )}
                  />
                  {sidebarOpen && (
                    <span className="ml-3 truncate">{item.name}</span>
                  )}
                </Link>
              )
            })}
          </nav>

          {/* Sidebar toggle button */}
          <div className="flex-shrink-0 p-4 border-t border-gray-200">
            <button
              type="button"
              className="hidden lg:flex items-center justify-center w-full p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-500 rounded-md transition-colors"
              onClick={toggleSidebar}
            >
              <Menu className="h-5 w-5" />
              {sidebarOpen && <span className="ml-2">Contraer</span>}
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top navigation */}
        <header className="bg-white border-b border-gray-200 px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            {/* Mobile menu button */}
            <button
              type="button"
              className="p-1.5 rounded-md text-gray-400 hover:bg-gray-100 hover:text-gray-500 lg:hidden"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="h-5 w-5" />
            </button>

            {/* Search bar - visible on larger screens */}
            <div className="hidden md:block flex-1 max-w-lg">
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Search className="h-4 w-4 text-gray-400" />
                </div>
                <input
                  type="text"
                  placeholder="Buscar análisis..."
                  className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500 text-sm"
                />
              </div>
            </div>

            {/* Right side */}
            <div className="flex items-center space-x-4">
              {/* Notifications */}
              <button
                type="button"
                className="p-1.5 rounded-md text-gray-400 hover:bg-gray-100 hover:text-gray-500"
              >
                <Bell className="h-5 w-5" />
              </button>

              {/* User menu */}
              <div className="relative" data-user-menu>
                <button
                  type="button"
                  className="flex items-center space-x-3 p-1.5 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                >
                  <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center">
                    <User className="h-4 w-4 text-white" />
                  </div>
                  <div className="hidden md:block text-left">
                    <p className="font-medium text-gray-700">{user?.name}</p>
                    <p className="text-xs text-gray-500">{user?.role}</p>
                  </div>
                  <ChevronDown className="h-4 w-4 text-gray-400" />
                </button>

                {/* User dropdown menu */}
                {userMenuOpen && (
                  <div className="absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50">
                    <div className="py-1">
                      <div className="px-4 py-2 text-sm text-gray-700 border-b border-gray-100">
                        <p className="font-medium">{user?.name}</p>
                        <p className="text-xs text-gray-500">{user?.email}</p>
                      </div>
                      <Link
                        to={routes.app.profile}
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        onClick={() => setUserMenuOpen(false)}
                      >
                        <User className="inline h-4 w-4 mr-2" />
                        Mi Perfil
                      </Link>
                      <Link
                        to={routes.app.settings}
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        onClick={() => setUserMenuOpen(false)}
                      >
                        <Settings className="inline h-4 w-4 mr-2" />
                        Configuración
                      </Link>
                      <div className="border-t border-gray-100">
                        <button
                          type="button"
                          className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          onClick={handleLogout}
                        >
                          <LogOut className="inline h-4 w-4 mr-2" />
                          Cerrar Sesión
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto px-4 py-6 sm:px-6 lg:px-8" style={{ backgroundColor: '#F5F5F5' }}>
          {children}
        </main>
      </div>
    </div>
  )
}

export default AppLayout