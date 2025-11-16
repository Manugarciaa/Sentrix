import React, { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/auth'
import { useTheme } from '@/hooks/useTheme'
import { Logo } from '@/components/ui/Logo'
import { routes } from '@/lib/config'
import { cn } from '@/lib/utils'
import { Sidebar, SidebarBody, SidebarLink } from '@/components/ui/Sidebar'
import { motion } from 'framer-motion'
import { showToast } from '@/lib/toast'
import {
  LayoutDashboard,
  Search,
  LogOut,
  User,
  Moon,
  Sun,
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
  const { theme, toggleTheme } = useTheme()

  const navigation: NavigationItem[] = [
    { name: 'Dashboard', href: routes.app.dashboard, icon: LayoutDashboard },
    { name: 'Análisis', href: routes.app.analysis, icon: Search },
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
    // Navigate to login page instead of home
    navigate(routes.public.login, { replace: true })

    // Show toast after a brief delay to ensure it appears on the login page
    setTimeout(() => {
      showToast.success('Sesión cerrada', 'Has cerrado sesión exitosamente', { duration: 2500 })
    }, 100)
  }

  // Build links for sidebar
  const links = filteredNavigation.map(item => {
    const Icon = item.icon
    const active = isActive(item.href)
    return {
      label: item.name,
      href: item.href,
      icon: (
        <Icon
          className={cn(
            'h-5 w-5 flex-shrink-0 transition-colors',
            active ? 'text-primary' : 'text-neutral-700 dark:text-neutral-200'
          )}
        />
      ),
    }
  })

  return (
    <div className="flex flex-col md:flex-row w-full h-screen overflow-hidden bg-primary/5 dark:bg-primary/10">
      <Sidebar open={true} setOpen={() => {}}>
        <SidebarBody className="justify-between gap-10">
          <div className="flex flex-1 flex-col overflow-y-auto overflow-x-hidden">
            {/* Logo */}
            <div className="mb-4">
              <LogoExpanded />
            </div>

            {/* Navigation Links */}
            <div className="flex flex-col gap-1">
              {links.map((link, idx) => (
                <SidebarLink
                  key={idx}
                  link={link}
                  className={cn(
                    isActive(link.href) &&
                      'bg-primary/10 dark:bg-primary/20 text-primary border-l-4 border-primary'
                  )}
                />
              ))}
            </div>
          </div>

          {/* Bottom Section - User + Theme + Logout */}
          <div className="flex flex-col gap-1 pt-4 border-t border-border">
            {/* User Info */}
            <div className="flex items-center gap-3 py-2.5 px-3 rounded-lg hover:bg-muted/50 transition-colors cursor-default">
              <div className="h-5 w-5 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center flex-shrink-0">
                <User className="h-3 w-3 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-foreground truncate">
                  {user?.display_name || user?.email || 'Usuario'}
                </p>
              </div>
            </div>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className={cn(
                'flex items-center gap-3 group/sidebar py-2.5 px-3 rounded-lg',
                'hover:bg-muted transition-all duration-200',
                'text-foreground',
                'justify-start'
              )}
            >
              {theme === 'dark' ? (
                <Sun className="h-5 w-5 flex-shrink-0" />
              ) : (
                <Moon className="h-5 w-5 flex-shrink-0" />
              )}
              <span className="text-sm font-medium whitespace-pre truncate">
                {theme === 'dark' ? 'Modo Claro' : 'Modo Oscuro'}
              </span>
            </button>

            {/* Logout Button */}
            <button
              onClick={handleLogout}
              className={cn(
                'flex items-center gap-3 group/sidebar py-2.5 px-3 rounded-lg',
                'hover:bg-red-50 dark:hover:bg-red-950/30 transition-all duration-200',
                'text-red-600 dark:text-red-400',
                'justify-start'
              )}
            >
              <LogOut className="h-5 w-5 flex-shrink-0" />
              <span className="text-sm font-medium whitespace-pre truncate">
                Cerrar Sesión
              </span>
            </button>
          </div>
        </SidebarBody>
      </Sidebar>

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col overflow-hidden">

        {/* Main Content - Scrollable */}
        <main className="flex-1 overflow-y-auto bg-primary/5 dark:bg-primary/10">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2, ease: 'easeInOut' }}
            className="w-full h-full p-4 sm:p-6 lg:p-8"
          >
            {children}
          </motion.div>
        </main>
      </div>
    </div>
  )
}

// Logo component
const LogoExpanded = () => {
  return (
    <Link
      to={routes.app.dashboard}
      className="relative z-20 flex items-center justify-center py-1"
    >
      <Logo className="h-8" />
    </Link>
  )
}

export default AppLayout
